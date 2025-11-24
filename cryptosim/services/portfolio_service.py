from collections import defaultdict
from models.transaction import Transaction
from models.coin import Coin

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
