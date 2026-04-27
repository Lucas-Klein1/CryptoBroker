from models.database import Database
from models.coin import Coin
import time

STARTING_BALANCE = 100_000.0


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

    def get_portfolio_history(self, acc_id):
        """Berechnet den historischen Gesamtvermoegens-Verlauf des Accounts
        (Cash-Balance + Wert der gehaltenen Coins) anhand der Transaktionen
        und der gespeicherten Preis-History der einzelnen Coins.
        Gibt eine Liste von {timestamp, value} zurueck, sortiert nach Zeitstempel."""

        conn = Database.get_connection()
        cur = conn.cursor()

        # Alle Transaktionen des Accounts, älteste zuerst
        cur.execute("""
            SELECT coin_id, type, amount, price, timestamp
            FROM transactions
            WHERE acc_id = ?
            ORDER BY timestamp ASC
        """, (acc_id,))
        txs = cur.fetchall()

        if not txs:
            conn.close()
            return []

        # Bestimme alle Coins im Portfolio
        coin_ids = list({row["coin_id"] for row in txs})

        # Lade History-Daten für alle relevanten Coins
        coin_histories = {}
        for coin_id in coin_ids:
            table = f"{coin_id.lower().replace('-', '_')}_history"
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cur.fetchone():
                cur.execute(
                    f"SELECT timestamp_ms, price FROM {table} ORDER BY timestamp_ms ASC"
                )
                coin_histories[coin_id] = [
                    (row["timestamp_ms"], row["price"]) for row in cur.fetchall()
                ]
            else:
                coin_histories[coin_id] = []

        conn.close()

        import bisect

        # Effizienter Preis-Lookup per binaerer Suche
        price_ts   = {cid: [h[0] for h in hist] for cid, hist in coin_histories.items()}
        price_vals = {cid: [h[1] for h in hist] for cid, hist in coin_histories.items()}

        def get_price_at(coin_id, ts):
            ts_list = price_ts.get(coin_id, [])
            if not ts_list:
                return None
            idx = bisect.bisect_right(ts_list, ts) - 1
            if idx < 0:
                return None
            return price_vals[coin_id][idx]

        # Timestamps: alle History-Punkte ab der ersten Transaktion.
        # Transaktions-Timestamps werden NICHT als eigene Chartpunkte aufgenommen,
        # damit pro Tag nur ein Datenpunkt entsteht (statt mehrerer bei Tagen mit
        # vielen Transaktionen). Die Schleife unten wendet alle Transaktionen
        # bis zum jeweiligen Timestamp ohnehin korrekt an.
        first_tx_ts = min(row["timestamp"] for row in txs)

        all_timestamps = set()
        for hist in coin_histories.values():
            for h_ts, _ in hist:
                if h_ts >= first_tx_ts:
                    all_timestamps.add(h_ts)

        all_timestamps = sorted(all_timestamps)

        # Startpunkt: Direkt vor der ersten Transaktion war das Vermoegen
        # gleich dem Startkapital (nur Cash, keine Coins).
        portfolio_history = [
            {"timestamp": first_tx_ts - 1, "value": STARTING_BALANCE}
        ]
        holdings = {}
        balance = STARTING_BALANCE
        tx_index = 0
        tx_list = list(txs)

        for ts in all_timestamps:
            # Alle Transaktionen bis einschliesslich dieses Timestamps anwenden
            while tx_index < len(tx_list) and tx_list[tx_index]["timestamp"] <= ts:
                tx = tx_list[tx_index]
                cid = tx["coin_id"]
                if tx["type"].upper() == "BUY":
                    holdings[cid] = holdings.get(cid, 0.0) + tx["amount"]
                    balance -= tx["amount"] * tx["price"]
                else:
                    holdings[cid] = holdings.get(cid, 0.0) - tx["amount"]
                    balance += tx["amount"] * tx["price"]
                tx_index += 1

            # Gesamtvermoegen berechnen: Cash-Balance + Wert aller Coin-Bestaende
            total = balance
            for cid, amount in holdings.items():
                if amount < 1e-9:
                    continue
                price = get_price_at(cid, ts)
                if price is not None:
                    total += amount * price

            portfolio_history.append({"timestamp": ts, "value": total})

        # Endpunkt: aktueller Stand mit den jetzigen Coin-Preisen,
        # damit das Chart-Ende exakt zum angezeigten Gesamtvermoegen passt.
        # Vorher noch alle Transaktionen anwenden, die nach dem letzten
        # History-Punkt liegen (oder alle, falls all_timestamps leer war).
        while tx_index < len(tx_list):
            tx = tx_list[tx_index]
            cid = tx["coin_id"]
            if tx["type"].upper() == "BUY":
                holdings[cid] = holdings.get(cid, 0.0) + tx["amount"]
                balance -= tx["amount"] * tx["price"]
            else:
                holdings[cid] = holdings.get(cid, 0.0) - tx["amount"]
                balance += tx["amount"] * tx["price"]
            tx_index += 1

        now_ts = int(time.time() * 1000)
        last_ts = all_timestamps[-1] if all_timestamps else first_tx_ts
        if now_ts > last_ts:
            total_now = balance
            for cid, amount in holdings.items():
                if amount < 1e-9:
                    continue
                coin = Coin.get_by_id(cid)
                if coin is not None and coin.current_price is not None:
                    total_now += amount * coin.current_price
            portfolio_history.append({"timestamp": now_ts, "value": total_now})

        return portfolio_history

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

    def get_balance(self, acc_id):
        """Berechnet die verfügbare Euro-Balance des Accounts.
        Startkapital 100.000 € minus alle Käufe plus alle Verkäufe."""
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
        net = row["net"] if row["net"] is not None else 0.0
        return STARTING_BALANCE + net

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

        if action == "BUY":
            cost = amount * coin.current_price
            balance = self.get_balance(acc_id)
            if cost > balance:
                raise ValueError(
                    f"Nicht genug Guthaben. Kosten: {cost:,.2f} €, "
                    f"Verfügbar: {balance:,.2f} €"
                )

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
