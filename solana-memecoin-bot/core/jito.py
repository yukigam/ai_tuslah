import aiohttp
import base64
from solders.transaction import VersionedTransaction
from config.settings import settings
from loguru import logger


class JitoClient:
    def __init__(self):
        self.engine = settings.jito_block_engine_url.rstrip("/")
        self.tip = settings.jito_tip_lamports

    async def send_bundle(self, txs: list[VersionedTransaction], trade_sol: float = 0.0) -> str | None:
        if not settings.jito_enabled:
            return None
        tip = self.tip
        if trade_sol > 0:
            from strategy.risk_manager import risk_manager
            tip = risk_manager.cap_fee(tip, trade_sol)
        # attach tip? assume tip already in txs; just log
        serialized = [base64.b64encode(bytes(t)).decode() for t in txs]
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendBundle",
            "params": [serialized, {"encoding": "base64"}],
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.engine}/api/v1/bundles", json=payload) as r:
                data = await r.json()
                if "result" in data:
                    logger.info(f"Jito bundle sent: {data['result']} (tip {tip})")
                    return data["result"]
                logger.error(f"Jito bundle error: {data}")
                return None

    async def get_bundle_status(self, bundle_id: str):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getBundleStatuses", "params": [[bundle_id]]}
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.engine}/api/v1/bundles", json=payload) as r:
                return await r.json()


jito = JitoClient()
