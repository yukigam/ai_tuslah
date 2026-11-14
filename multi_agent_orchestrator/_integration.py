"""Integration layer for existing project scripts."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List


class ScriptIntegration:
    """Integration layer for existing project scripts."""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    async def process_facebook_post(self, message: str, use_ai: bool = True) -> Dict:
        """Process Facebook post through orchestrator."""
        task = {
            "type": "post_generation",
            "content_type": "post",
            "prompt": message,
            "style": "engaging",
            "target": "facebook",
        }
        result = await self.orchestrator.delegate(task)
        return result

    async def debug_script(self, script_code: str) -> Dict:
        """Debug a script through the code agent."""
        task = {
            "type": "fix_indentation",
            "code": script_code,
            "language": "python",
        }
        result = await self.orchestrator.delegate(task)
        return result

    async def check_database_state(self, query_type: str = "check_database") -> Dict:
        """Check database state through data agent."""
        task = {
            "type": "check_database",
            "query_type": query_type,
        }
        result = await self.orchestrator.delegate(task)
        return result

    async def concurrent_task_processing(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process multiple tasks concurrently."""
        return await self.orchestrator.execute_concurrent(tasks)