import pytest
import sqlite3
from models.database import Database


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch, tmp_path):
    db_path = str(tmp_path / "test.db")

    def get_connection():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT UNIQUE NOT NULL,
            pw         TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS coins (
            id                          TEXT PRIMARY KEY,
            symbol                      TEXT,
            name                        TEXT,
            image                       TEXT,
            current_price               REAL,
            market_cap                  INTEGER,
            market_cap_rank             INTEGER,
            price_change_24h            REAL,
            price_change_percentage_24h REAL
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id   TEXT,
            acc_id    INTEGER,
            price     REAL,
            amount    REAL,
            type      TEXT,
            timestamp INTEGER
        );
    """)
    conn.commit()
    conn.close()

    monkeypatch.setattr(Database, "get_connection", staticmethod(get_connection))


@pytest.fixture
def test_account(in_memory_db):
    from models.account import Account
    conn = Database.get_connection()
    conn.execute("INSERT INTO accounts (name, pw) VALUES (?, ?)", ("testuser", "hashed_pw"))
    conn.commit()
    row = conn.execute("SELECT * FROM accounts WHERE name = ?", ("testuser",)).fetchone()
    conn.close()
    return Account.from_row(row)


@pytest.fixture
def test_coin(in_memory_db):
    from models.coin import Coin
    conn = Database.get_connection()
    conn.execute(
        "INSERT INTO coins (id, symbol, name, current_price, market_cap, market_cap_rank, image,"
        " price_change_24h, price_change_percentage_24h)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        ("bitcoin", "BTC", "Bitcoin", 50000.0, 1_000_000_000, 1, "", 500.0, 1.0),
    )
    conn.commit()
    conn.close()
    return Coin.get_by_id("bitcoin")
