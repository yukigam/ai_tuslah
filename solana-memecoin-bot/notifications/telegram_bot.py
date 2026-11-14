import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config.settings import settings
from loguru import logger


class TelegramNotifier:
    def __init__(self):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.bot = None
        self.app = None
        self.executor = None
        self.copier = None
        if self.token:
            self.app = Application.builder().token(self.token).build()
            self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CallbackQueryHandler(self.on_button))

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_menu(update.effective_chat.id)

    async def _send_menu(self, chat_id):
        keyboard = [
            [InlineKeyboardButton("💰 Balance & PnL", callback_data="balance")],
            [InlineKeyboardButton("📄/🔴 Toggle Paper/Live", callback_data="toggle_mode")],
            [InlineKeyboardButton("➕ Add Wallet", callback_data="add_wallet"),
             InlineKeyboardButton("➖ Remove Wallet", callback_data="remove_wallet")],
            [InlineKeyboardButton("⏸ Pause", callback_data="pause"),
             InlineKeyboardButton("▶️ Resume", callback_data="resume")],
        ]
        await self.app.bot.send_message(chat_id=chat_id, text="Solana Memecoin Bot", reply_markup=InlineKeyboardMarkup(keyboard))

    async def on_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        data = q.data
        if data == "balance":
            await q.edit_message_text("Balance & PnL: (connect RPC for live values)")
        elif data == "toggle_mode":
            settings.paper_mode = not settings.paper_mode
            settings.live_mode = not settings.paper_mode
            await q.edit_message_text(f"Mode toggled. PAPER={settings.paper_mode} LIVE={settings.live_mode}")
        elif data == "pause":
            if self.copier:
                self.copier.pause()
            await q.edit_message_text("Trading paused.")
        elif data == "resume":
            if self.copier:
                self.copier.resume()
            await q.edit_message_text("Trading resumed.")
        else:
            await q.edit_message_text(f"Action: {data}")

    async def send(self, text: str):
        if not self.app or not self.chat_id:
            logger.info(f"[TG-disabled] {text}")
            return
        try:
            await self.app.bot.send_message(chat_id=self.chat_id, text=text)
        except Exception as e:
            logger.error(f"telegram send failed: {e}")

    async def run(self):
        if self.app:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
