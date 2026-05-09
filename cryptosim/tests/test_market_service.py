import pytest
from services.market_service import MarketService, STARTING_BALANCE


class TestGetBalance:
    """U1–U3: Balance-Berechnung aus Transaktionen"""

    def test_without_transactions_returns_starting_balance(self, test_account):
        svc = MarketService()
        assert svc.get_balance(test_account.id) == STARTING_BALANCE

    def test_after_buy_balance_decreases(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 1.0)
        expected = STARTING_BALANCE - (1.0 * test_coin.current_price)
        assert svc.get_balance(test_account.id) == pytest.approx(expected)

    def test_after_sell_balance_increases(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 2.0)
        balance_after_buy = svc.get_balance(test_account.id)
        svc.execute_trade(test_account.id, test_coin.id, "SELL", 1.0)
        assert svc.get_balance(test_account.id) == pytest.approx(
            balance_after_buy + (1.0 * test_coin.current_price)
        )


class TestGetPosition:
    """U4–U5: Positions-Berechnung (Crypto-Bestand)"""

    def test_after_buy_position_equals_amount(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 1.0)
        assert svc.get_position(test_account.id, test_coin.id) == pytest.approx(1.0)

    def test_after_full_sell_position_is_zero(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 2.0)
        svc.execute_trade(test_account.id, test_coin.id, "SELL", 2.0)
        assert svc.get_position(test_account.id, test_coin.id) == pytest.approx(0.0)


class TestExecuteTrade:
    """U6–U8: Trade-Validierung"""

    def test_buy_without_funds_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        too_many = (STARTING_BALANCE / test_coin.current_price) + 1
        with pytest.raises(ValueError):
            svc.execute_trade(test_account.id, test_coin.id, "BUY", too_many)

    def test_sell_without_position_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        with pytest.raises(ValueError):
            svc.execute_trade(test_account.id, test_coin.id, "SELL", 1.0)

    def test_invalid_action_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        with pytest.raises(ValueError):
            svc.execute_trade(test_account.id, test_coin.id, "HODL", 1.0)

    def test_unknown_coin_raises_value_error(self, test_account):
        svc = MarketService()
        with pytest.raises(ValueError):
            svc.execute_trade(test_account.id, "nonexistent-coin", "BUY", 1.0)


class TestGetHistory:
    """Historische Preisdaten"""

    def test_coin_without_history_table_returns_empty_list(self, test_coin):
        svc = MarketService()
        assert svc.get_history(test_coin.id) == []

    def test_nonexistent_coin_returns_empty_list(self):
        svc = MarketService()
        assert svc.get_history("nonexistent-coin") == []


class TestGetTransactions:
    """Transaktionshistorie"""

    def test_after_buy_returns_one_record_with_correct_data(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 0.5)
        txs = svc.get_transactions(test_account.id)
        assert len(txs) == 1
        assert txs[0]["type"] == "BUY"
        assert txs[0]["amount"] == pytest.approx(0.5)
        assert txs[0]["coin_id"] == test_coin.id


class TestGetTradedCoinIds:
    """Coins in denen ein Account jemals gehandelt hat"""

    def test_without_trades_returns_empty_list(self, test_account):
        svc = MarketService()
        assert svc.get_traded_coin_ids(test_account.id) == []

    def test_after_buy_contains_coin_id(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 1.0)
        assert test_coin.id in svc.get_traded_coin_ids(test_account.id)


class TestGetPortfolioHistory:
    """Portfolio-Verlauf über die Zeit"""

    def test_without_transactions_returns_empty(self, test_account):
        svc = MarketService()
        assert svc.get_portfolio_history(test_account.id) == []

    def test_with_buy_and_price_history_returns_value_series(self, test_account, test_coin):
        from models.database import Database
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 1.0)

        conn = Database.get_connection()
        tx_ts = conn.execute(
            "SELECT timestamp FROM transactions WHERE acc_id = ?", (test_account.id,)
        ).fetchone()["timestamp"]
        conn.close()

        conn = Database.get_connection()
        conn.execute("""
            CREATE TABLE bitcoin_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_ms INTEGER UNIQUE,
                price        REAL
            )
        """)
        conn.execute(
            "INSERT INTO bitcoin_history (timestamp_ms, price) VALUES (?, ?)",
            (tx_ts + 1000, 48000.0),
        )
        conn.commit()
        conn.close()

        result = svc.get_portfolio_history(test_account.id)
        assert len(result) >= 2
        assert result[0]["value"] == pytest.approx(STARTING_BALANCE)
