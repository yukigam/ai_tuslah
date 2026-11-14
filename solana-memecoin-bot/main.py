import asyncio
from loguru import logger
from config.settings import settings
from core.rpc_client import rpc
from core.wallet import load_keypair
from notifications.telegram_bot import TelegramNotifier
from execution.order_executor import OrderExecutor
from strategy.copy_trade import CopyTrader
from strategy.risk_manager import risk_manager

async def price_feed(token):
    # Placeholder: integrate DEX price API (DexScreener / Birdeye)
    return None

async def main():
    logger.info(f"Starting bot. PAPER_MODE={settings.paper_mode} LIVE_MODE={settings.live_mode}")
    notifier = TelegramNotifier()
    await notifier.send("🤖 Solana bot started")
    executor = OrderExecutor(rpc, notifier)

    # copy trading
    async def on_signal(sig):
        logger.info(f"Signal: {sig}")
    copier = CopyTrader(on_signal)
    asyncio.create_task(copier.run(rpc))
    asyncio.create_task(executor.monitor_positions(price_feed))

    try:
        while True:
            await asyncio.sleep(60)
    finally:
        await rpc.close()

if __name__ == "__main__":
    asyncio.run(main())
