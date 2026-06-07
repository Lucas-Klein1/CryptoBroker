from .database import Database

class Transaction:
    def __init__(self, id, coin_id, acc_id, price, amount, type, timestamp):
        self.id = id
        self.coin_id = coin_id
        self.acc_id = acc_id
        self.price = price
        self.amount = amount
        self.type = type
        self.timestamp = timestamp

    @staticmethod
    def from_row(row):
        return Transaction(
            id=row["id"],
            coin_id=row["coin_id"],
            acc_id=row["acc_id"],
            price=row["price"],
            amount=row["amount"],
            type=row["type"],
            timestamp=row["timestamp"],
        )

    @staticmethod
    def for_account(acc_id: int):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM transactions WHERE acc_id = ? ORDER BY timestamp ASC",
            (acc_id,),
        )
        rows = cur.fetchall()
        conn.close()
        return [Transaction.from_row(r) for r in rows]

    @staticmethod
    def for_account_with_coin_info(acc_id: int):
        """Liefert Transaktionen samt zugehoeriger Coin-Stammdaten (Name, Symbol, Bild),
        neueste zuerst."""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id, t.coin_id, t.type, t.amount, t.price, t.timestamp,
                   c.name, c.symbol, c.image
            FROM transactions t
            JOIN coins c ON c.id = t.coin_id
            WHERE t.acc_id = ?
            ORDER BY t.timestamp DESC
        """, (acc_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def net_position(acc_id: int, coin_id: str) -> float:
        """Saldo eines Coin-Bestands aus allen Kaeufen/Verkaeufen (in Coin-Einheiten)."""
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

    @staticmethod
    def net_cash_flow(acc_id: int) -> float:
        """Netto-Euro-Veraenderung durch alle Kaeufe/Verkaeufe eines Accounts
        (negativ bei Kaeufen, positiv bei Verkaeufen)."""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT SUM(
                CASE
                    WHEN type='BUY'  THEN -(amount * price)
                    WHEN type='SELL' THEN  (amount * price)
                    ELSE 0
                END
            ) AS net
            FROM transactions
            WHERE acc_id=?
        """, (acc_id,))
        row = cur.fetchone()
        conn.close()
        return float(row["net"] if row["net"] is not None else 0.0)

    @staticmethod
    def traded_coin_ids(acc_id: int):
        """Liefert alle Coin-IDs, in denen der Account jemals gehandelt hat."""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT coin_id FROM transactions WHERE acc_id = ?",
            (acc_id,),
        )
        rows = cur.fetchall()
        conn.close()
        return [row["coin_id"] for row in rows]

    @staticmethod
    def create(acc_id: int, coin_id: str, price: float, amount: float, type: str, timestamp: int):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (coin_id, acc_id, price, amount, type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (coin_id, acc_id, price, amount, type, timestamp))
        conn.commit()
        conn.close()
