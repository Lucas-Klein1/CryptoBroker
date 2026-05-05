from .database import Database


class Favorite:
    """Verwaltet Coin-Favoriten pro Account.

    Die Tabelle wird beim ersten Zugriff angelegt (kein separater
    Migrations-Schritt noetig). Primaerschluessel ist (acc_id, coin_id),
    sodass ein Coin pro Account nur einmal als Favorit gespeichert wird.
    """

    @staticmethod
    def _ensure_table(cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                acc_id  INTEGER NOT NULL,
                coin_id TEXT    NOT NULL,
                PRIMARY KEY (acc_id, coin_id)
            )
        """)

    @staticmethod
    def is_favorite(acc_id, coin_id) -> bool:
        if acc_id is None or coin_id is None:
            return False
        conn = Database.get_connection()
        cur = conn.cursor()
        Favorite._ensure_table(cur)
        cur.execute(
            "SELECT 1 FROM favorites WHERE acc_id = ? AND coin_id = ?",
            (acc_id, coin_id),
        )
        row = cur.fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def add(acc_id, coin_id):
        conn = Database.get_connection()
        cur = conn.cursor()
        Favorite._ensure_table(cur)
        cur.execute(
            "INSERT OR IGNORE INTO favorites (acc_id, coin_id) VALUES (?, ?)",
            (acc_id, coin_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def remove(acc_id, coin_id):
        conn = Database.get_connection()
        cur = conn.cursor()
        Favorite._ensure_table(cur)
        cur.execute(
            "DELETE FROM favorites WHERE acc_id = ? AND coin_id = ?",
            (acc_id, coin_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def toggle(acc_id, coin_id) -> bool:
        """Fuegt Favorit hinzu oder entfernt ihn. Gibt den neuen Status zurueck
        (True = jetzt Favorit, False = jetzt kein Favorit)."""
        if Favorite.is_favorite(acc_id, coin_id):
            Favorite.remove(acc_id, coin_id)
            return False
        Favorite.add(acc_id, coin_id)
        return True

    @staticmethod
    def get_for_account(acc_id):
        """Liefert alle Favoriten-Coins eines Accounts als Liste von Coin-Objekten,
        sortiert nach market_cap_rank. Coins, die in der coins-Tabelle nicht mehr
        existieren, werden uebersprungen."""
        if acc_id is None:
            return []
        conn = Database.get_connection()
        cur = conn.cursor()
        Favorite._ensure_table(cur)
        cur.execute("""
            SELECT c.id, c.name, c.symbol, c.current_price,
                   c.market_cap, c.market_cap_rank, c.image
            FROM favorites f
            JOIN coins c ON c.id = f.coin_id
            WHERE f.acc_id = ?
            ORDER BY c.market_cap_rank ASC
        """, (acc_id,))
        rows = cur.fetchall()
        conn.close()

        # Import hier, um Zirkularitaet zu vermeiden
        from .coin import Coin
        return [Coin(**row) for row in rows]