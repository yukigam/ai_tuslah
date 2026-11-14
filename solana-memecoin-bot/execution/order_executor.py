import asyncio, json, os, time
from config.settings import settings
from loguru import logger
from core.wallet import load_keypair
from strategy.risk_manager import Position, risk_manager


class PositionTracker:
    def __init__(self, path=settings.db_path):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.positions: dict[str, Position] = {}

    def open(self, pos: Position):
        self.positions[pos.token] = pos

    def close(self, token: str):
        return self.positions.pop(token, None)

    def get(self, token: str):
        return self.positions.get(token)

    def all(self):
        return list(self.positions.values())


class OrderExecutor:
    def __init__(self, rpc, notifier=None):
        self.rpc = rpc
        self.notifier = notifier
        self.tracker = PositionTracker()
        self.paper_log = "logs/paper_trades.jsonl"

    async def buy(self, token: str, price: float, amount_sol: float = 0.0, balance_sol: float | None = None):
        if amount_sol <= 0:
            if balance_sol is None:
                kp = load_keypair()
                if kp:
                    balance_sol = await self.rpc.get_balance(kp.pubkey())
                else:
                    balance_sol = settings.max_position_sol + 0.01
            amount_sol = risk_manager.position_size_sol(balance_sol)
        if amount_sol <= 0:
            logger.warning(f"Insufficient balance for trade on {token}; skipping")
            return None
        if not risk_manager.has_enough_for_fees(balance_sol if balance_sol is not None else amount_sol + 0.005, amount_sol):
            logger.warning(f"Not enough SOL reserve for fees/rent for {token}; skipping trade")
            return None
        if settings.paper_mode and not settings.live_mode:
            pos = Position(token=token, entry_price=price, amount=amount_sol / price, sol_spent=amount_sol, peak_price=price)
            self.tracker.open(pos)
            self._paper_log({"action": "buy", "token": token, "price": price, "sol": amount_sol, "ts": time.time()})
            logger.info(f"[PAPER] BUY {token} @ {price} for {amount_sol} SOL")
            if self.notifier:
                await self.notifier.send(f"📄 PAPER BUY {token} @ {price} ({amount_sol} SOL)")
            return pos
        logger.warning("Live execution not fully implemented; use paper mode")
        return None

    async def sell(self, token: str, price: float, reason: str = "", amount: float | None = None):
        pos = self.tracker.get(token)
        if not pos:
            return None
        sell_amount = amount if amount is not None else pos.amount
        pnl = (price - pos.entry_price) / pos.entry_price * 100
        sol_received = sell_amount * price
        if amount is None or amount >= pos.amount:
            self.tracker.close(token)
        else:
            pos.amount -= sell_amount
        if settings.paper_mode and not settings.live_mode:
            self._paper_log({"action": "sell", "token": token, "price": price, "amount": sell_amount, "pnl_pct": pnl, "reason": reason, "ts": time.time()})
            logger.info(f"[PAPER] SELL {sell_amount} {token} @ {price} PnL {pnl:.2f}% ({reason})")
            if self.notifier:
                await self.notifier.send(f"📄 PAPER SELL {token} @ {price} PnL {pnl:.2f}% ({reason})")
        risk_manager.record_loss(pos.sol_spent - sol_received) if amount is None else None
        return pnl

    async def take_profit(self, token: str, price: float):
        pos = self.tracker.get(token)
        if not pos:
            return None
        # Liquidate initial position size to recover principal, retain moonbag
        moonbag = risk_manager.moonbag_amount(pos)
        sell_amount = max(pos.amount - moonbag, 0.0)
        await self.sell(token, price, "TP-2x (principal recovered)", amount=sell_amount)
        if self.notifier:
            await self.notifier.send(f"🌙 Moonbag retained: {moonbag} {token}")

    def _paper_log(self, rec):
        os.makedirs("logs", exist_ok=True)
        with open(self.paper_log, "a") as f:
            f.write(json.dumps(rec) + "\n")

    async def monitor_positions(self, price_feed):
        while True:
            for pos in list(self.tracker.all()):
                price = await price_feed(pos.token)
                if price is None:
                    continue
                if risk_manager.should_take_profit(pos, price):
                    await self.take_profit(pos.token, price)
                elif risk_manager.should_stop_loss(pos, price):
                    await self.sell(pos.token, price, "SL")
                elif risk_manager.update_trailing(pos, price):
                    await self.sell(pos.token, price, "TRAILING")
            await asyncio.sleep(3)
