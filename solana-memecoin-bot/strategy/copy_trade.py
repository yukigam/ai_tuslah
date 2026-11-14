import asyncio
from config.settings import settings
from loguru import logger
from solana.rpc.async_api import AsyncClient


class CopyTrader:
    def __init__(self, on_signal):
        self.on_signal = on_signal
        self.seen = set()
        self._running = True

    async def _get_signatures(self, rpc, wallet: str):
        try:
            if isinstance(rpc, AsyncClient):
                resp = await rpc.get_signatures_for_address(wallet, limit=10)
            else:
                resp = await rpc.call("get_signatures_for_address", wallet, {"limit": 10})
            return resp.value if hasattr(resp, "value") else (resp.get("value") if isinstance(resp, dict) else None)
        except Exception as e:
            logger.error(f"copy poll error {wallet}: {e}")
            return None

    async def poll_wallet(self, rpc, wallet: str):
        try:
            sigs = await self._get_signatures(rpc, wallet)
            for sig_info in (sigs or []):
                sig = str(sig_info.signature if hasattr(sig_info, "signature") else sig_info.get("signature"))
                if sig in self.seen:
                    continue
                self.seen.add(sig)
                await self.on_signal({"type": "copy", "wallet": wallet, "signature": sig})
        except Exception as e:
            logger.error(f"copy poll error {wallet}: {e}")

    async def run(self, rpc):
        while self._running:
            for w in list(settings.copy_wallets):
                await self.poll_wallet(rpc, w)
            await asyncio.sleep(5)

    def pause(self):
        self._running = False

    def resume(self):
        self._running = True
