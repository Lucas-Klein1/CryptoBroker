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
