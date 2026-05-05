import pytest
from services.market_service import MarketService, STARTING_BALANCE


class TestTradeFlow:
    """I1–I2: Vollständige Trade-Szenarien über mehrere Operationen"""

    def test_buy_sell_cycle_restores_balance(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 2.0)
        svc.execute_trade(test_account.id, test_coin.id, "SELL", 2.0)
        assert svc.get_balance(test_account.id) == pytest.approx(STARTING_BALANCE)

    def test_multiple_buys_accumulate_position(self, test_account, test_coin):
        svc = MarketService()
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 0.5)
        svc.execute_trade(test_account.id, test_coin.id, "BUY", 0.5)
        assert svc.get_position(test_account.id, test_coin.id) == pytest.approx(1.0)
