import requests
from models.database import Database
from datetime import datetime


class CoinSyncService:
    def update_coins_table(self):
        """Aktualisiert coins-Tabelle mit aktuellen Daten von CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "eur",
                "x_cg_demo_api_key": "CG-Nv8tfrfQovH51o4NZQw3TjjK"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            conn = Database.get_connection()
            cursor = conn.cursor()

            # Tabelle neu erstellen (wie bisher)
            cursor.execute("DROP TABLE IF EXISTS coins")
            cursor.execute("""
            CREATE TABLE coins (
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
            conn.commit()

            for coin in data:
                cursor.execute("""
                INSERT INTO coins VALUES (
                    :id, :symbol, :name, :image, :current_price, :market_cap,
                    :market_cap_rank, :fully_diluted_valuation, :total_volume,
                    :high_24h, :low_24h, :price_change_24h, :price_change_percentage_24h,
                    :market_cap_change_24h, :market_cap_change_percentage_24h,
                    :circulating_supply, :total_supply, :max_supply,
                    :ath, :ath_change_percentage, :ath_date,
                    :atl, :atl_change_percentage, :atl_date, :last_updated
                )
                """, coin)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print("Fehler beim Coin-Sync:", e)
            return False

    def sync_coin_history(self, coin_id, days=365):
        """
        Synchronisiert die History für einen Coin inkrementell.
        - Lädt nur fehlende Tage
        - Überschreibt bestehende Daten NICHT
        
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
            
            # 2. Finde den ältesten Datenpunkt
            cursor.execute(f"SELECT MIN(timestamp_ms) FROM {table_name}")
            result = cursor.fetchone()
            oldest_timestamp = result[0] if result and result[0] else None
            
            # 3. Berechne Zeitraum
            end_timestamp = int(datetime.now().timestamp() * 1000)
            
            if oldest_timestamp:
                # Bereits Daten vorhanden: Hole alles ab einem Tag vor dem ältesten Datenpunkt
                start_timestamp = oldest_timestamp - (24 * 60 * 60 * 1000)
            else:
                # Keine Daten: Hole die letzten X Tage
                start_timestamp = end_timestamp - (days * 24 * 60 * 60 * 1000)
            
            # 4. Lade Daten vom API
            history_data = self._fetch_coin_history(coin_id, start_timestamp, end_timestamp)
            
            if not history_data:
                conn.close()
                return 0
            
            # 5. Schreibe nur neue Einträge (UNIQUE verhindert Duplikate!)
            new_entries = 0
            for entry in history_data:
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
                print(f"ℹ️ {coin_id}: Daten sind aktuell")
            
            return new_entries
        
        except Exception as e:
            print(f"Fehler beim Synchronisieren von {coin_id}: {e}")
            return 0

    def _fetch_coin_history(self, coin_id, start_timestamp, end_timestamp):
        """
        Ruft historische Daten von CoinGecko ab
        
        Args:
            coin_id: Die Coin-ID (z.B. 'bitcoin')
            start_timestamp: Startzeitpunkt in Millisekunden
            end_timestamp: Endzeitpunkt in Millisekunden
        
        Returns:
            Liste mit Einträgen: [{'timestamp_ms': 1704067200000, 'price': 42000}, ...]
        """
        try:
            history_data = []
            current_start = start_timestamp
            
            # CoinGecko hat ein Limit von ~365 Tagen pro Request
            while current_start < end_timestamp:
                current_end = min(
                    current_start + (365 * 24 * 60 * 60 * 1000),
                    end_timestamp
                )
                
                url = "https://api.coingecko.com/api/v3/coins/{}/market_chart".format(coin_id)
                params = {
                    "vs_currency": "eur",
                    "days": "365",
                    "x_cg_demo_api_key": "CG-Nv8tfrfQovH51o4NZQw3TjjK"
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Verarbeite die Daten
                if 'prices' in data:
                    for price_data in data['prices']:
                        timestamp_ms = price_data[0]  # CoinGecko gibt Millisekunden
                        price = price_data[1]
                        
                        history_data.append({
                            'timestamp_ms': timestamp_ms,
                            'price': price
                        })
                
                # Nächster Request
                current_start = current_end
            
            return history_data
        
        except Exception as e:
            print(f"Fehler beim Abrufen der History für {coin_id}: {e}")
            return []