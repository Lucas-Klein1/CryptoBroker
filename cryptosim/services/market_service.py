from models.database import Database
from models.coin import Coin
import time


class MarketService:

    def get_all_coins(self):
        return Coin.get_all()

    def get_history(self, coin_id):
        coin = Coin.get_by_id(coin_id)
        if coin is None:
            return []

        table = f"{coin.id.lower().replace('-', '_')}_history"

        conn = Database.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        exists = cur.fetchone()

        if not exists:
            conn.close()
            return []

        cur.execute(f"SELECT timestamp_ms, price FROM {table} ORDER BY timestamp_ms ASC")
        rows = cur.fetchall()
        conn.close()

        return [
            {"timestamp": row["timestamp_ms"], "price": row["price"]}
            for row in rows
        ]

    def get_position(self, acc_id, coin_id):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT SUM(
                CASE 
                    WHEN type='BUY' THEN amount
                    WHEN type='SELL' THEN -amount
                    ELSE 0
                END
            ) AS balance
            FROM transactions
            WHERE acc_id=? AND coin_id=?
        """, (acc_id, coin_id))
        row = cur.fetchone()
        conn.close()

        return float(row["balance"] if row["balance"] is not None else 0)

    def execute_trade(self, acc_id, coin_id, action, amount):
        action = action.upper()
        if action not in ("BUY", "SELL"):
            raise ValueError("Ungültige Aktion.")

        coin = Coin.get_by_id(coin_id)
        if coin is None:
            raise ValueError("Coin nicht gefunden.")

        if action == "SELL":
            current = self.get_position(acc_id, coin_id)
            if amount > current:
                raise ValueError("Zu wenig Bestand für Verkauf.")

        price = coin.current_price
        ts = int(time.time() * 1000)

        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (coin_id, acc_id, price, amount, type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (coin_id, acc_id, price, amount, action, ts))
        conn.commit()
        conn.close()

    def get_transactions(self, acc_id):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id,
                   t.coin_id,
                   t.type,
                   t.amount,
                   t.price,
                   t.timestamp,
                   c.name,
                   c.symbol,
                   c.image
            FROM transactions t
            JOIN coins c ON c.id = t.coin_id
            WHERE t.acc_id = ?
            ORDER BY t.timestamp DESC
        """, (acc_id,))
        rows = cur.fetchall()
        conn.close()

        txs = []
        for r in rows:
            total = r["amount"] * r["price"]
            txs.append({
                "id": r["id"],
                "coin_id": r["coin_id"],
                "coin_name": r["name"],
                "symbol": r["symbol"],
                "type": r["type"],
                "amount": r["amount"],
                "price": r["price"],
                "total": total,
                "ts": r["timestamp"],
                "image": r["image"],
            })

        return txs
