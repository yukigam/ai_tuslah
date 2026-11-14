"""
Base class for all agents in the orchestrator.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List


class BaseAgent(ABC):
    """Base class for all agents in the orchestrator."""

    def __init__(self, name: str, agent_id: str):
        self.name = name
        self.agent_id = agent_id
        self.capabilities: List[str] = []
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return result dict."""
        pass

    def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle a given task type."""
        return task_type in self.capabilities

    def report_success(self):
        self.execution_count += 1
        self.success_count += 1

    def report_failure(self):
        self.execution_count += 1
        self.failure_count += 1