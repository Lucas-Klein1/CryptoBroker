import pytest
from models.database import Database
from services.market_service import MarketService, STARTING_BALANCE, MIN_TRADE_EUR


@pytest.fixture
def zero_price_coin(in_memory_db):
    from models.coin import Coin
    conn = Database.get_connection()
    conn.execute(
        "INSERT INTO coins (id, symbol, name, current_price, market_cap, market_cap_rank, image,"
        " price_change_24h, price_change_percentage_24h)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        ("zero-coin", "ZRO", "Zero", 0.0, 1_000, 99, "", 0.0, 0.0),
    )
    conn.commit()
    conn.close()
    return Coin.get_by_id("zero-coin")


class TestPlaceOrderModes:
    """Eingabe-Wert wird je nach Modus korrekt in eine Coin-Menge umgerechnet."""

    def test_amount_mode_uses_value_as_quantity(self, test_account, test_coin):
        svc = MarketService()
        coin, amount = svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "0.1")
        assert coin.id == test_coin.id
        assert amount == pytest.approx(0.1)
        assert svc.get_position(test_account.id, test_coin.id) == pytest.approx(0.1)

    def test_eur_mode_converts_euro_amount_to_quantity(self, test_account, test_coin):
        svc = MarketService()
        coin, amount = svc.place_order(test_account.id, test_coin.id, "BUY", "EUR", "5000")
        assert amount == pytest.approx(5000 / test_coin.current_price)

    def test_percent_mode_sells_share_of_current_position(self, test_account, test_coin):
        svc = MarketService()
        svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "1.0")

        coin, amount = svc.place_order(test_account.id, test_coin.id, "SELL", "PERCENT", "50")

        assert amount == pytest.approx(0.5)
        assert svc.get_position(test_account.id, test_coin.id) == pytest.approx(0.5)

    def test_comma_is_accepted_as_decimal_separator(self, test_account, test_coin):
        svc = MarketService()
        coin, amount = svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "0,5")
        assert amount == pytest.approx(0.5)

    def test_unknown_mode_falls_back_to_amount(self, test_account, test_coin):
        svc = MarketService()
        coin, amount = svc.place_order(test_account.id, test_coin.id, "BUY", "WHATEVER", "0.2")
        assert amount == pytest.approx(0.2)


class TestPlaceOrderInputValidation:
    """U: Eingabe-Validierung (Parsing, Wertebereich, Coin/Preis-Existenz)."""

    def test_non_numeric_value_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        with pytest.raises(ValueError, match="Ungültige Eingabe"):
            svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "abc")

    def test_zero_value_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        with pytest.raises(ValueError, match="größer als 0"):
            svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "0")

    def test_negative_value_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        with pytest.raises(ValueError, match="größer als 0"):
            svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "-1")

    def test_unknown_coin_raises_value_error(self, test_account):
        svc = MarketService()
        with pytest.raises(ValueError, match="Coin nicht gefunden"):
            svc.place_order(test_account.id, "nonexistent-coin", "BUY", "AMOUNT", "1")

    def test_zero_price_coin_raises_value_error(self, test_account, zero_price_coin):
        svc = MarketService()
        with pytest.raises(ValueError, match="Ungültiger Preis"):
            svc.place_order(test_account.id, zero_price_coin.id, "BUY", "AMOUNT", "1")

    def test_below_minimum_trade_value_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        too_small_amount = (MIN_TRADE_EUR / test_coin.current_price) / 2
        with pytest.raises(ValueError, match="Mindestbetrag"):
            svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", str(too_small_amount))


class TestPlaceOrderPercentMode:
    """U: Sonderregeln des PERCENT-Modus (nur Verkauf, max. 100%, Bestand vorhanden)."""

    def test_percent_on_buy_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        with pytest.raises(ValueError, match="nur beim Verkauf"):
            svc.place_order(test_account.id, test_coin.id, "BUY", "PERCENT", "50")

    def test_percent_above_100_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "1.0")
        with pytest.raises(ValueError, match="maximal 100"):
            svc.place_order(test_account.id, test_coin.id, "SELL", "PERCENT", "150")

    def test_percent_without_position_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        with pytest.raises(ValueError, match="keine Anteile"):
            svc.place_order(test_account.id, test_coin.id, "SELL", "PERCENT", "50")


class TestPlaceOrderTradeRules:
    """Bestehende Trade-Regeln (Guthaben/Bestand) greifen weiterhin ueber place_order."""

    def test_buy_without_funds_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        too_many = (STARTING_BALANCE / test_coin.current_price) + 1
        with pytest.raises(ValueError, match="Nicht genug Guthaben"):
            svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", str(too_many))

    def test_sell_more_than_position_raises_value_error(self, test_account, test_coin):
        svc = MarketService()
        svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "1.0")
        with pytest.raises(ValueError, match="Zu wenig Bestand"):
            svc.place_order(test_account.id, test_coin.id, "SELL", "AMOUNT", "2.0")

    def test_successful_order_persists_transaction(self, test_account, test_coin):
        svc = MarketService()
        svc.place_order(test_account.id, test_coin.id, "BUY", "AMOUNT", "0.5")

        txs = svc.get_transactions(test_account.id)
        assert len(txs) == 1
        assert txs[0]["type"] == "BUY"
        assert txs[0]["amount"] == pytest.approx(0.5)
        assert txs[0]["price"] == pytest.approx(test_coin.current_price)
