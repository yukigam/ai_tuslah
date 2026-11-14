"""
Core orchestrator that delegates tasks to specialized agents.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List


class Orchestrator:
    """Core orchestrator that delegates tasks to specialized agents."""

    def __init__(self, name: str = "Orchestrator"):
        self.name = name
        self.agents: Dict[str, "BaseAgent"] = {}
        self.task_history: List[Dict] = []
        self.max_concurrent = 5
        self.validation_steps: List[str] = []

    def register_agent(self, agent: "BaseAgent"):
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        print(f"[ORCH] Registered agent: {agent.name} ({agent.agent_id})")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"[ORCH] Unregistered agent: {agent_id}")

    async def delegate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate a task to the appropriate agent."""
        task_type = task.get("type", "")
        task_id = task.get("id", f"task-{int(time.time())}")

        # Find matching agent
        matching_agent = None
        for agent in self.agents.values():
            if agent.can_handle(task_type):
                matching_agent = agent
                break

        if not matching_agent:
            return {
                "status": "error",
                "error": f"No agent found for task type: {task_type}",
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Execute with timing
        start_time = time.time()
        self.task_history.append(
            {"task_id": task_id, "type": task_type, "agent": matching_agent.name}
        )

        try:
            result = await matching_agent.execute(task)
            elapsed = time.time() - start_time

            result.update(
                {
                    "task_id": task_id,
                    "agent_name": matching_agent.name,
                    "execution_time": round(elapsed, 3),
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            matching_agent.report_success()
            print(
                f"[ORCH] ✅ Task {task_id} completed by {matching_agent.name} "
                f"in {result.get('execution_time')}s"
            )
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            error_result = {
                "status": "error",
                "error": str(e),
                "task_id": task_id,
                "agent_name": matching_agent.name,
                "execution_time": round(elapsed, 3),
                "timestamp": datetime.utcnow().isoformat(),
            }
            matching_agent.report_failure()
            print(f"[ORCH] ❌ Task {task_id} failed: {e}")
            return error_result

    async def execute_concurrent(
        self, tasks: List[Dict[str, Any]], validate: bool = True
    ) -> List[Dict[str, Any]]:
        """Execute multiple tasks concurrently with optional validation."""
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def limited_execute(task):
            async with semaphore:
                result = await self.delegate(task)
                return result

        results = await asyncio.gather(
            *[limited_execute(t) for t in tasks], return_exceptions=True
        )

        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "status": "error",
                        "error": str(result),
                        "task_id": tasks[i].get("id", f"task-{i}"),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            else:
                processed_results.append(result)

        if validate:
            processed_results = await self._validate_results(processed_results)

        return processed_results

    async def _validate_results(self, results: List[Dict]) -> List[Dict]:
        """Validate results from agent executions."""
        validated = []
        for result in results:
            if result.get("status") == "error":
                validated.append(
                    {
                        "status": "validation_failed",
                        "error": result.get("error"),
                        "original_status": "error",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            elif result.get("status") == "completed":
                result["validated_at"] = datetime.utcnow().isoformat()
                validated.append(result)
            else:
                validated.append(result)
        return validated

    def get_agent_stats(self) -> Dict[str, Dict]:
        """Get statistics for all registered agents."""
        stats = {}
        for agent_id, agent in self.agents.items():
            stats[agent_id] = {
                "name": agent.name,
                "capabilities": agent.capabilities,
                "execution_count": agent.execution_count,
                "success_count": agent.success_count,
                "failure_count": agent.failure_count,
                "success_rate": (
                    agent.success_count / agent.execution_count
                    if agent.execution_count > 0
                    else 0
                ),
            }
        return stats