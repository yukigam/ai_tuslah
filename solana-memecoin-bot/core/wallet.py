from solders.keypair import Keypair
from config.settings import settings


def load_keypair() -> Keypair | None:
    key = settings.wallet_private_key
    if not key:
        return None
    try:
        import base58
        raw = base58.b58decode(key)
        return Keypair.from_bytes(raw)
    except Exception:
        # try JSON array
        import json
        arr = json.loads(key)
        return Keypair.from_bytes(bytes(arr))
