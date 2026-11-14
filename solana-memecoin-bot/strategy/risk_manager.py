from dataclasses import dataclass, field
from config.settings import settings


# Micro-capital constants
MIN_SOL_RESERVE = 0.005  # keep untouched for fees + rent
MICRO_TRADE_SOL = 0.005  # ~$1 at ~$200/SOL
MAX_MICRO_TRADE_SOL = 0.01  # ~$2
FEE_CAP_PERCENT_OF_TRADE = 0.05  # fees <= 5% of trade size
TAKE_PROFIT_MULTIPLIER = 2.0  # 2x = 100% gain
MOONBAG_PERCENT = 0.15  # retain 10-20% of holdings
TRAILING_STOP_PERCENT = 15.0  # 15-20% drop from local peak


@dataclass
class Position:
    token: str
    entry_price: float
    amount: float  # in token units
    sol_spent: float
    peak_price: float = field(default=0.0)


class RiskManager:
    def __init__(self):
        self.daily_loss_sol = 0.0

    def position_size_sol(self, balance_sol: float) -> float:
        spendable = max(balance_sol - MIN_SOL_RESERVE, 0.0)
        if spendable <= 0:
            return 0.0
        size = min(MICRO_TRADE_SOL, spendable, settings.max_position_sol)
        size = max(size, 0.0)
        size = min(size, MAX_MICRO_TRADE_SOL)
        return size

    def has_enough_for_fees(self, balance_sol: float, trade_sol: float) -> bool:
        return (balance_sol - trade_sol) >= MIN_SOL_RESERVE

    def cap_fee(self, fee_lamports: int, trade_sol: float) -> int:
        trade_lamports = int(trade_sol * 1e9)
        cap = int(trade_lamports * FEE_CAP_PERCENT_OF_TRADE)
        return min(fee_lamports, cap)

    def check_slippage(self, expected: float, actual: float) -> bool:
        if expected <= 0:
            return True
        slip = abs(actual - expected) / expected * 100
        return slip <= settings.max_slippage_percent

    def should_take_profit(self, pos: Position, price: float) -> bool:
        return price >= pos.entry_price * TAKE_PROFIT_MULTIPLIER

    def moonbag_amount(self, pos: Position) -> float:
        return pos.amount * MOONBAG_PERCENT

    def should_stop_loss(self, pos: Position, price: float) -> bool:
        loss = (pos.entry_price - price) / pos.entry_price * 100
        return loss >= settings.stop_loss_percent

    def update_trailing(self, pos: Position, price: float) -> bool:
        if price > pos.peak_price:
            pos.peak_price = price
        if pos.peak_price <= 0:
            return False
        drop = (pos.peak_price - price) / pos.peak_price * 100
        return drop >= TRAILING_STOP_PERCENT

    def daily_loss_exceeded(self) -> bool:
        return self.daily_loss_sol >= settings.daily_loss_limit_sol

    def record_loss(self, sol: float):
        if sol < 0:
            self.daily_loss_sol += -sol


risk_manager = RiskManager()
