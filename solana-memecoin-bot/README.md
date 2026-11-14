# Solana Memecoin & Crypto Trading Bot

## Setup
1. Copy `.env.example` to `.env` and fill values.
2. `python -m venv venv && venv\\Scripts\\activate` (Windows) or `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python main.py`

## Paper trading
Default `PAPER_MODE=true`. Trades are simulated and logged to `logs/paper_trades.jsonl`. No real funds spent.

## Live trading
Set `PAPER_MODE=false` and `LIVE_MODE=true`, add `WALLET_PRIVATE_KEY`. Use a private RPC. Start small.

## VPS (Oracle Cloud free tier)
- Create Ubuntu 22.04 instance, open port 8080 for Axiom webhooks.
- Run `deploy/setup_vps.sh`, edit `.env`, `sudo cp deploy/solana-bot.service /etc/systemd/system/`, then `sudo systemctl enable --now solana-bot`.
- Monitor: `journalctl -u solana-bot -f`.

## Safety notes
- Never commit `.env`.
- Default slippage 10%, max position 0.5 SOL, daily loss limit 2 SOL.
- Live execution paths are stubs; integrate Raydium/Pump.fun SDKs before going live.
