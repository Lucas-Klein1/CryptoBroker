import requests
from models.database import Database


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
