from .database import Database
import bcrypt

# Mindestanforderungen an Passwörter
MIN_PW_LENGTH = 8


def validate_password(pw: str):
    """Prüft Passwortanforderungen. Wirft ValueError bei Verstoß."""
    if len(pw) < MIN_PW_LENGTH:
        raise ValueError(f"Passwort muss mindestens {MIN_PW_LENGTH} Zeichen lang sein.")
    if not any(c.isupper() for c in pw):
        raise ValueError("Passwort muss mindestens einen Großbuchstaben enthalten.")
    if not any(c.isdigit() for c in pw):
        raise ValueError("Passwort muss mindestens eine Zahl enthalten.")


def _hash_password(pw: str) -> bytes:
    """Erzeugt einen bcrypt-Hash aus einem Klartextpasswort."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw.encode("utf-8"), salt)


def _password_matches(pw: str, stored_hash) -> bool:
    """Prueft ein Klartextpasswort gegen den gespeicherten Hash.
    Faellt fuer Alt-Daten auf einen Klartextvergleich zurueck."""
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), stored_hash)
    except Exception:
        return pw == stored_hash


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
        validate_password(pw)
        hashed_password = _hash_password(pw)
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
        existing = Account.get_by_name(name)
        if existing is None:
            return Account.create(name, pw)
        if not _password_matches(pw, existing.pw):
            raise ValueError("Falsches Passwort.")
        return existing

    def change_password(self, old_pw: str, new_pw: str):
        """Ändert das Passwort nach Verifikation des alten Passworts."""
        if not _password_matches(old_pw, self.pw):
            raise ValueError("Aktuelles Passwort ist falsch.")
        validate_password(new_pw)
        self._update_password(_hash_password(new_pw))

    def _update_password(self, hashed: bytes):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET pw = ? WHERE id = ?", (hashed, self.id))
        conn.commit()
        conn.close()
        self.pw = hashed