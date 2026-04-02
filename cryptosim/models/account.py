from .database import Database
import bcrypt

class Account:
    def __init__(self, id, name, pw, created_at):
        self.id = id
        self.name = name
        self.pw = pw
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        return Account(
            id=row["id"],
            name=row["name"],
            pw=row["pw"],
            created_at=row["created_at"],
        )

    @staticmethod
    def get_by_id(acc_id: int):
        if acc_id is None:
            return None
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE id = ?", (acc_id,))
        row = cur.fetchone()
        conn.close()
        return Account.from_row(row) if row else None

    @staticmethod
    def get_by_name(name: str):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()
        return Account.from_row(row) if row else None

    @staticmethod
    def create(name: str, pw: str):
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(pw.encode("utf-8"), salt)
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO accounts (name, pw) VALUES (?, ?)",
            (name, hashed_password),
        )
        conn.commit()
        acc_id = cur.lastrowid
        conn.close()
        return Account.get_by_id(acc_id)

    @staticmethod
    def login_or_register(name: str, pw: str):
        acc = Account.get_by_name(name)
        if acc:
            try:
                if not bcrypt.checkpw(pw.encode("utf-8"), acc.pw):
                    raise ValueError("Falsches Passwort")
                return acc
            except: 
                if not pw == acc.pw:
                    raise ValueError("Falsches Passwort")
                return acc
        # Falls nicht existiert -> registrieren
        return Account.create(name, pw)