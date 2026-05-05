from models.database import Database
from models.coin import Coin
import bisect
import time

STARTING_BALANCE = 100_000.0


class MarketService:

    # ---------- Coins / History ----------

    def get_all_coins(self):
        return Coin.get_all()

    def get_history(self, coin_id):
        coin = Coin.get_by_id(coin_id)
        if coin is None:
            return []
        history = self._load_coin_history(coin.id)
        return [{"timestamp": ts, "price": price} for ts, price in history]

    def get_traded_coin_ids(self, acc_id):
        """Liefert alle Coin-IDs, in denen der Account jemals getradet hat.
        Dient als Quelle fuer das Portfolio-History-Sync (alle Coins, die in
        den Portfolio-Chart einfliessen)."""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT coin_id FROM transactions WHERE acc_id = ?",
            (acc_id,),
        )
        rows = cur.fetchall()
        conn.close()
        return [row["coin_id"] for row in rows]

    # ---------- Portfolio-Verlauf (Integration) ----------

    def get_portfolio_history(self, acc_id):
        """Gesamtvermoegen-Verlauf (Cash + Coin-Werte) ueber die Zeit."""
        txs = self._load_transactions(acc_id)
        if not txs:
            return []

        coin_histories = self._load_histories_for_transactions(txs)
        timeline = self._build_timeline(txs, coin_histories)
        portfolio_history = self._compute_portfolio_values(txs, coin_histories, timeline)
        self._append_current_value(portfolio_history, txs, coin_histories)
        return portfolio_history

    # ---------- Trading ----------

    def execute_trade(self, acc_id, coin_id, action, amount):
        action = self._normalize_action(action)
        coin = self._require_coin(coin_id)
        self._validate_trade(acc_id, coin, action, amount)
        self._save_transaction(acc_id, coin, action, amount)

    # ---------- Account-Stand ----------

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
        """Verfuegbares Euro-Guthaben: Startkapital - Kaeufe + Verkaeufe."""
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

    def get_transactions(self, acc_id):
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
        return [self._row_to_transaction_dict(r) for r in rows]

    # ====================================================================
    # Private Hilfsmethoden (Operations)
    # ====================================================================

    @staticmethod
    def _history_table_name(coin_id):
        """Eine zentrale Stelle fuer die Tabellennamen-Konvention (DRY)."""
        return f"{coin_id.lower().replace('-', '_')}_history"

    def _load_coin_history(self, coin_id):
        """Liefert [(timestamp_ms, price), ...] oder [] wenn keine Tabelle existiert."""
        table = self._history_table_name(coin_id)
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        )
        if not cur.fetchone():
            conn.close()
            return []
        cur.execute(f"SELECT timestamp_ms, price FROM {table} ORDER BY timestamp_ms ASC")
        rows = cur.fetchall()
        conn.close()
        return [(row["timestamp_ms"], row["price"]) for row in rows]

    def _load_transactions(self, acc_id):
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT coin_id, type, amount, price, timestamp
            FROM transactions
            WHERE acc_id = ?
            ORDER BY timestamp ASC
        """, (acc_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _load_histories_for_transactions(self, txs):
        coin_ids = {tx["coin_id"] for tx in txs}
        return {cid: self._load_coin_history(cid) for cid in coin_ids}

    @staticmethod
    def _build_timeline(txs, coin_histories):
        first_tx_ts = min(tx["timestamp"] for tx in txs)
        timestamps = set()
        for hist in coin_histories.values():
            for ts, _ in hist:
                if ts >= first_tx_ts:
                    timestamps.add(ts)
        return sorted(timestamps)

    def _compute_portfolio_values(self, txs, coin_histories, timeline):
        first_tx_ts = min(tx["timestamp"] for tx in txs)
        price_lookup = self._build_price_lookup(coin_histories)

        portfolio_history = [{"timestamp": first_tx_ts - 1, "value": STARTING_BALANCE}]
        holdings, balance = {}, STARTING_BALANCE
        tx_index = 0

        for ts in timeline:
            tx_index, balance = self._apply_transactions_until(
                txs, tx_index, ts, holdings, balance
            )
            total = self._total_value(balance, holdings, price_lookup, ts)
            portfolio_history.append({"timestamp": ts, "value": total})

        return portfolio_history

    def _append_current_value(self, portfolio_history, txs, coin_histories):
        """Endpunkt mit aktuellen Coin-Preisen anhaengen, damit das Chart-Ende
        zum angezeigten Gesamtvermoegen passt."""
        timeline = self._build_timeline(txs, coin_histories)
        first_tx_ts = min(tx["timestamp"] for tx in txs)
        price_lookup = self._build_price_lookup(coin_histories)

        # Alle Transaktionen erneut anwenden, um den aktuellen Stand zu kennen.
        holdings, balance = {}, STARTING_BALANCE
        for tx in txs:
            balance = self._apply_single_transaction(tx, holdings, balance)

        now_ts = int(time.time() * 1000)
        last_ts = timeline[-1] if timeline else first_tx_ts
        if now_ts <= last_ts:
            return

        total_now = balance
        for cid, amount in holdings.items():
            if amount < 1e-9:
                continue
            coin = Coin.get_by_id(cid)
            if coin is not None and coin.current_price is not None:
                total_now += amount * coin.current_price
        portfolio_history.append({"timestamp": now_ts, "value": total_now})

    @staticmethod
    def _apply_single_transaction(tx, holdings, balance):
        """Wendet eine Transaktion auf holdings/balance an (zentrale BUY/SELL-Logik, DRY)."""
        cid = tx["coin_id"]
        amount = tx["amount"]
        price = tx["price"]
        if tx["type"].upper() == "BUY":
            holdings[cid] = holdings.get(cid, 0.0) + amount
            balance -= amount * price
        else:
            holdings[cid] = holdings.get(cid, 0.0) - amount
            balance += amount * price
        return balance

    def _apply_transactions_until(self, txs, tx_index, ts, holdings, balance):
        while tx_index < len(txs) and txs[tx_index]["timestamp"] <= ts:
            balance = self._apply_single_transaction(txs[tx_index], holdings, balance)
            tx_index += 1
        return tx_index, balance

    @staticmethod
    def _build_price_lookup(coin_histories):
        """Baut eine Closure fuer effiziente Preis-Lookups per binaerer Suche."""
        price_ts = {cid: [h[0] for h in hist] for cid, hist in coin_histories.items()}
        price_vals = {cid: [h[1] for h in hist] for cid, hist in coin_histories.items()}

        def get_price_at(coin_id, ts):
            ts_list = price_ts.get(coin_id, [])
            if not ts_list:
                return None
            idx = bisect.bisect_right(ts_list, ts) - 1
            if idx < 0:
                return None
            return price_vals[coin_id][idx]

        return get_price_at

    @staticmethod
    def _total_value(balance, holdings, price_lookup, ts):
        total = balance
        for cid, amount in holdings.items():
            if amount < 1e-9:
                continue
            price = price_lookup(cid, ts)
            if price is not None:
                total += amount * price
        return total

    # ---------- Trading-Hilfsmethoden ----------

    @staticmethod
    def _normalize_action(action):
        action = action.upper()
        if action not in ("BUY", "SELL"):
            raise ValueError("Ungültige Aktion.")
        return action

    @staticmethod
    def _require_coin(coin_id):
        coin = Coin.get_by_id(coin_id)
        if coin is None:
            raise ValueError("Coin nicht gefunden.")
        return coin

    def _validate_trade(self, acc_id, coin, action, amount):
        if action == "SELL":
            current = self.get_position(acc_id, coin.id)
            if amount > current:
                raise ValueError("Zu wenig Bestand für Verkauf.")
        elif action == "BUY":
            cost = amount * coin.current_price
            balance = self.get_balance(acc_id)
            if cost > balance:
                raise ValueError(
                    f"Nicht genug Guthaben. Kosten: {cost:,.2f} €, "
                    f"Verfügbar: {balance:,.2f} €"
                )

    @staticmethod
    def _save_transaction(acc_id, coin, action, amount):
        ts = int(time.time() * 1000)
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (coin_id, acc_id, price, amount, type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (coin.id, acc_id, coin.current_price, amount, action, ts))
        conn.commit()
        conn.close()

    @staticmethod
    def _row_to_transaction_dict(r):
        return {
            "id": r["id"],
            "coin_id": r["coin_id"],
            "coin_name": r["name"],
            "symbol": r["symbol"],
            "type": r["type"],
            "amount": r["amount"],
            "price": r["price"],
            "total": r["amount"] * r["price"],
            "ts": r["timestamp"],
            "image": r["image"],
        }