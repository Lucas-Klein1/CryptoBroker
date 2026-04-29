from collections import defaultdict
from models.transaction import Transaction
from models.coin import Coin
from models.database import Database
from services.market_service import STARTING_BALANCE


class PortfolioService:
    def get_portfolio_overview(self, acc_id: int):
        txs = Transaction.for_account(acc_id)
        # Coin-Bestände aufsummieren
        amounts = defaultdict(float)
        for tx in txs:
            if tx.type.upper() == "BUY":
                amounts[tx.coin_id] += tx.amount
            elif tx.type.upper() == "SELL":
                amounts[tx.coin_id] -= tx.amount

        positions = []
        total_value = 0.0

        for coin_id, amount in amounts.items():
            if abs(amount) < 1e-9:
                continue
            coin = Coin.get_by_id(coin_id)
            value = amount * coin.current_price
            total_value += value
            positions.append(
                {
                    "coin": coin,
                    "amount": amount,
                    "value": value,
                }
            )

        return positions, total_value

    def get_leaderboard(self):
        """Berechnet das Gesamtvermoegen (Cash + Coin-Werte zu aktuellen Preisen)
        aller Accounts und gibt eine sortierte Bestenliste zurueck.

        Returns:
            Liste von Dicts: [{"rank": 1, "name": "...", "balance": ..., "coin_value": ..., "total": ...}, ...]
        """
        conn = Database.get_connection()
        cur = conn.cursor()

        # Alle Accounts laden
        cur.execute("SELECT id, name FROM accounts")
        accounts = cur.fetchall()

        # Aktuelle Coin-Preise einmalig laden (Lookup)
        cur.execute("SELECT id, current_price FROM coins")
        price_lookup = {row["id"]: row["current_price"] for row in cur.fetchall()}

        # Alle Transaktionen einmal laden, dann nach Account gruppieren
        cur.execute("""
            SELECT acc_id, coin_id, type, amount, price
            FROM transactions
        """)
        tx_rows = cur.fetchall()
        conn.close()

        # Pro Account: Cash-Saldo und Coin-Bestaende
        cash_by_acc = defaultdict(lambda: STARTING_BALANCE)
        holdings_by_acc = defaultdict(lambda: defaultdict(float))

        for r in tx_rows:
            acc_id = r["acc_id"]
            coin_id = r["coin_id"]
            amount = r["amount"]
            price = r["price"]
            t = (r["type"] or "").upper()
            if t == "BUY":
                cash_by_acc[acc_id] -= amount * price
                holdings_by_acc[acc_id][coin_id] += amount
            elif t == "SELL":
                cash_by_acc[acc_id] += amount * price
                holdings_by_acc[acc_id][coin_id] -= amount

        # Ergebnis-Liste aufbauen
        entries = []
        for acc in accounts:
            acc_id = acc["id"]
            balance = cash_by_acc[acc_id]
            holdings = holdings_by_acc[acc_id]

            coin_value = 0.0
            for coin_id, amount in holdings.items():
                if abs(amount) < 1e-9:
                    continue
                price = price_lookup.get(coin_id)
                if price is not None:
                    coin_value += amount * price

            total = balance + coin_value
            entries.append({
                "acc_id": acc_id,
                "name": acc["name"],
                "balance": balance,
                "coin_value": coin_value,
                "total": total,
            })

        # Sortieren absteigend nach Gesamtvermoegen, Rang vergeben
        entries.sort(key=lambda e: e["total"], reverse=True)
        for i, e in enumerate(entries, start=1):
            e["rank"] = i

        return entries