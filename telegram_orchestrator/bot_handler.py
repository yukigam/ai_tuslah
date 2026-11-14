"""Telegram Bot Handler using Orchestrator Integration."""

import asyncio
from typing import List, Tuple

from multi_agent_orchestrator.telegram_orchestrator.integration_core import (
    TelegramOrchestratorIntegration,
)


class TelegramBotHandler:
    """Telegram bot message handler using the Orchestrator."""
    
    def __init__(self, integration: TelegramOrchestratorIntegration):
        self.integration = integration
    
    async def process_message(self, user_id: int, message_text: str, chat_id: int) -> str:
        """Process a single Telegram message through the orchestrator."""
        return await self.integration.handle_message(user_id, message_text, chat_id)
    
    async def process_concurrent_messages(
        self, messages: List[Tuple[int, str]], chat_id: int
    ) -> List[str]:
        """Process multiple messages concurrently."""
        tasks = [
            self.integration.handle_message(user_id, msg, chat_id)
            for user_id, msg in messages
        ]
        return await asyncio.gather(*tasks)