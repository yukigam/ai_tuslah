import asyncio
import aiohttp
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from config.settings import settings
from loguru import logger


class RpcClient:
    def __init__(self):
        self.urls = [settings.solana_rpc_url, settings.solana_rpc_fallback]
        self._idx = 0
        self.client = AsyncClient(self.urls[0])

    async def _failover(self):
        self._idx = (self._idx + 1) % len(self.urls)
        await self.client.close()
        self.client = AsyncClient(self.urls[self._idx])
        logger.warning(f"Switched RPC to {self.urls[self._idx]}")

    async def call(self, method, *args, **kwargs):
        for _ in range(len(self.urls)):
            try:
                fn = getattr(self.client, method)
                return await fn(*args, **kwargs)
            except Exception as e:
                logger.warning(f"RPC {method} failed on {self.urls[self._idx]}: {e}")
                await self._failover()
        raise RuntimeError(f"All RPC endpoints failed for {method}")

    async def get_priority_fee(self, trade_sol: float = 0.0) -> int:
        try:
            resp = await self.client.get_recent_prioritization_fees()
            fees = [r.prioritization_fee for r in resp.value] if resp.value else []
            if not fees:
                return 0
            fees.sort()
            idx = int(len(fees) * settings.priority_fee_percentile / 100)
            idx = min(idx, len(fees) - 1)
            fee = fees[idx]
            fee = min(fee, settings.max_priority_fee_lamports)
            if trade_sol > 0:
                from strategy.risk_manager import risk_manager
                fee = risk_manager.cap_fee(fee, trade_sol)
            return fee
        except Exception as e:
            logger.warning(f"priority fee fetch failed: {e}")
            return 0

    async def get_balance(self, pubkey: Pubkey) -> float:
        r = await self.call("get_balance", pubkey)
        return r.value / 1e9

    async def close(self):
        await self.client.close()


rpc = RpcClient()
