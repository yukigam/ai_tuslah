"""Telegram Orchestrator Integration Package.

Integration layer between Telegram Bot and Multi-Agent Orchestrator.
Routes incoming user messages through the Orchestrator which delegates
to specialized agents based on message content/intent.
"""

from multi_agent_orchestrator._orchestrator import Orchestrator
from multi_agent_orchestrator._content_agent import ContentAgent
from multi_agent_orchestrator._code_debug_agent import CodeDebugAgent
from multi_agent_orchestrator._data_agent import DataAgent
from multi_agent_orchestrator._integration import ScriptIntegration

__all__ = [
    'TelegramOrchestratorIntegration',
    'TelegramBotHandler',
]