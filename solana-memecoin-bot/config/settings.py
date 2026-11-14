import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _env(key, default=None):
    v = os.getenv(key, default)
    return v.strip() if isinstance(v, str) else v


class Settings(BaseModel):
    solana_rpc_url: str = Field(default_factory=lambda: _env("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"))
    solana_rpc_fallback: str = Field(default_factory=lambda: _env("SOLANA_RPC_FALLBACK", "https://solana-rpc.publicnode.com"))
    wallet_private_key: str = Field(default_factory=lambda: _env("WALLET_PRIVATE_KEY", ""))
    jito_block_engine_url: str = Field(default_factory=lambda: _env("JITO_BLOCK_ENGINE_URL", "https://mainnet.block-engine.jito.wtf"))
    jito_tip_lamports: int = Field(default_factory=lambda: int(_env("JITO_TIP_LAMPORTS", "50000")))
    jito_enabled: bool = Field(default_factory=lambda: _env("JITO_ENABLED", "true").lower() == "true")
    priority_fee_percentile: int = Field(default_factory=lambda: int(_env("PRIORITY_FEE_PERCENTILE", "75")))
    max_priority_fee_lamports: int = Field(default_factory=lambda: int(_env("MAX_PRIORITY_FEE_LAMPORTS", "250000")))
    paper_mode: bool = Field(default_factory=lambda: _env("PAPER_MODE", "true").lower() == "true")
    live_mode: bool = Field(default_factory=lambda: _env("LIVE_MODE", "false").lower() == "true")
    max_position_sol: float = Field(default_factory=lambda: float(_env("MAX_POSITION_SOL", "0.01")))
    max_slippage_percent: float = Field(default_factory=lambda: float(_env("MAX_SLIPPAGE_PERCENT", "10")))
    take_profit_percent: float = Field(default_factory=lambda: float(_env("TAKE_PROFIT_PERCENT", "50")))
    stop_loss_percent: float = Field(default_factory=lambda: float(_env("STOP_LOSS_PERCENT", "20")))
    trailing_stop_percent: float = Field(default_factory=lambda: float(_env("TRAILING_STOP_PERCENT", "10")))
    daily_loss_limit_sol: float = Field(default_factory=lambda: float(_env("DAILY_LOSS_LIMIT_SOL", "0.005")))
    copy_wallets: list = Field(default_factory=lambda: [w.strip() for w in _env("COPY_WALLETS", "").split(",") if w.strip()])
    copy_amount_sol: float = Field(default_factory=lambda: float(_env("COPY_AMOUNT_SOL", "0.005")))
    telegram_bot_token: str = Field(default_factory=lambda: _env("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = Field(default_factory=lambda: _env("TELEGRAM_CHAT_ID", ""))
    axiom_webhook_port: int = Field(default_factory=lambda: int(_env("AXIOM_WEBHOOK_PORT", "8080")))
    axiom_webhook_secret: str = Field(default_factory=lambda: _env("AXIOM_WEBHOOK_SECRET", ""))
    db_path: str = Field(default_factory=lambda: _env("DB_PATH", "./data/positions.db"))

    def validate_live(self):
        if self.live_mode and not self.wallet_private_key:
            raise ValueError("LIVE_MODE requires WALLET_PRIVATE_KEY")
        if self.live_mode and self.paper_mode:
            raise ValueError("Cannot have both PAPER_MODE and LIVE_MODE true")


settings = Settings()
settings.validate_live()
ROOT_PATH = ROOT
