from models.database import Database

class Coin:
    def __init__(self, id, name, symbol, current_price, market_cap, market_cap_rank, image,
                 price_change_24h=None, price_change_percentage_24h=None):
        self.id = id
        self.name = name
        self.symbol = symbol
        self.current_price = current_price
        self.market_cap = market_cap
        self.market_cap_rank = market_cap_rank
        self.image = image
        self.price_change_24h = price_change_24h
        self.price_change_percentage_24h = price_change_percentage_24h

    @staticmethod
    def get_all():
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, symbol, current_price, market_cap, market_cap_rank, image,
                   price_change_24h, price_change_percentage_24h
            FROM coins
            ORDER BY market_cap_rank ASC
        """)
        rows = cur.fetchall()
        conn.close()
        return [Coin(**row) for row in rows]

    @staticmethod
    def get_by_id(coin_id):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, symbol, current_price, market_cap, market_cap_rank, image,
                   price_change_24h, price_change_percentage_24h
            FROM coins
            WHERE id = ?
        """, (coin_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Coin(**row)
        return None
