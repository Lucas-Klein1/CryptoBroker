import requests
from models.database import Database
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from current directory

secret = os.getenv("SECRET_KEY")

MS_PER_DAY = 24 * 60 * 60 * 1000


def _today_midnight_utc_ms() -> int:
    """Liefert den Unix-Timestamp (ms) von heute 00:00 UTC."""
    now = datetime.now(timezone.utc)
    midnight = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    return int(midnight.timestamp() * 1000)


class CoinSyncService:
    def update_coins_table(self):
        """Aktualisiert coins-Tabelle mit aktuellen Daten von CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "eur",
                "x_cg_demo_api_key": secret
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS coins (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                name TEXT,
                image TEXT,
                current_price REAL,
                market_cap INTEGER,
                market_cap_rank INTEGER,
                fully_diluted_valuation INTEGER,
                total_volume INTEGER,
                high_24h REAL,
                low_24h REAL,
                price_change_24h REAL,
                price_change_percentage_24h REAL,
                market_cap_change_24h REAL,
                market_cap_change_percentage_24h REAL,
                circulating_supply REAL,
                total_supply REAL,
                max_supply REAL,
                ath REAL,
                ath_change_percentage REAL,
                ath_date TEXT,
                atl REAL,
                atl_change_percentage REAL,
                atl_date TEXT,
                last_updated TEXT
            )
            """)

            api_ids = [coin["id"] for coin in data]

            for coin in data:
                cursor.execute("""
                INSERT OR REPLACE INTO coins VALUES (
                    :id, :symbol, :name, :image, :current_price, :market_cap,
                    :market_cap_rank, :fully_diluted_valuation, :total_volume,
                    :high_24h, :low_24h, :price_change_24h, :price_change_percentage_24h,
                    :market_cap_change_24h, :market_cap_change_percentage_24h,
                    :circulating_supply, :total_supply, :max_supply,
                    :ath, :ath_change_percentage, :ath_date,
                    :atl, :atl_change_percentage, :atl_date, :last_updated
                )
                """, coin)

            placeholders = ",".join("?" * len(api_ids))
            cursor.execute(f"DELETE FROM coins WHERE id NOT IN ({placeholders})", api_ids)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print("Fehler beim Coin-Sync:", e)
            return False

    def sync_coin_history(self, coin_id):
        """
        Synchronisiert die History für einen Coin inkrementell.
        - Lädt nur fehlende Tage
        - Überschreibt bestehende Daten NICHT
        - Spart API-Calls: Wenn fuer heute (00:00 UTC) bereits ein Eintrag
          existiert, wird gar nicht erst die API angefragt.

        Args:
            coin_id: Die Coin-ID (z.B. 'bitcoin')
            days: Wie viele Tage maximal zurück (Standard: 1 Jahr)

        Returns:
            Anzahl neuer Einträge die hinzugefügt wurden
        """
        try:
            table_name = f"{coin_id.lower().replace('-', '_')}_history"

            conn = Database.get_connection()
            cursor = conn.cursor()

            # 1. Prüfe: Existiert die Tabelle schon?
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                # Neue Tabelle erstellen
                cursor.execute(f"""
                    CREATE TABLE {table_name} (
                        id INTEGER PRIMARY KEY,
                        timestamp_ms INTEGER UNIQUE NOT NULL,
                        price REAL NOT NULL
                    )
                """)
                conn.commit()
                print(f"History-Tabelle erstellt: {table_name}")

            # 1b. Frueher Abbruch: Wenn fuer den heutigen Tag (00:00 UTC) schon
            #     ein Eintrag existiert, ist die History "fuer heute" aktuell.
            #     Da Eintraege immer um 00:00 UTC liegen, ist das exakt der
            #     letzte erwartete Datenpunkt.
            today_ts = _today_midnight_utc_ms()
            cursor.execute(
                f"SELECT 1 FROM {table_name} WHERE timestamp_ms = ? LIMIT 1",
                (today_ts,)
            )
            if cursor.fetchone() is not None:
                conn.close()
                print(f"ℹ️ {coin_id}: Heutiger Wert bereits vorhanden, kein API-Call.")
                return 0

            history_data = self._fetch_coin_history(coin_id)

            if not history_data:
                conn.close()
                return 0

            # 5. Schreibe nur neue Einträge (UNIQUE verhindert Duplikate!)
            #    Nur exakte 00:00-UTC-Tagespunkte uebernehmen, damit die History
            #    eine konsistente Tagesgranularitaet behaelt.
            new_entries = 0
            for entry in history_data:
                if entry['timestamp_ms'] % MS_PER_DAY != 0:
                    continue
                try:
                    cursor.execute(f"""
                        INSERT INTO {table_name} (timestamp_ms, price)
                        VALUES (?, ?)
                    """, (entry['timestamp_ms'], entry['price']))
                    new_entries += 1
                except Exception:
                    # UNIQUE Constraint verletzt → Datenpunkt existiert schon
                    pass

            conn.commit()
            conn.close()

            if new_entries > 0:
                print(f"{coin_id}: {new_entries} neue Einträge hinzugefügt")
            else:
                print(f"{coin_id}: Daten sind aktuell")

            return new_entries

        except Exception as e:
            print(f"Fehler beim Synchronisieren von {coin_id}: {e}")
            return 0

    def _fetch_coin_history(self, coin_id):
        try:
            url = "https://api.coingecko.com/api/v3/coins/{}/market_chart".format(coin_id)
            params = {
                "vs_currency": "eur",
                "days": "365",
                "x_cg_demo_api_key": secret
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'prices' not in data:
                return []

            return [
                {'timestamp_ms': p[0], 'price': p[1]}
                for p in data['prices']
            ]

        except Exception as e:
            print(f"Fehler beim Abrufen der History für {coin_id}: {e}")
            return []