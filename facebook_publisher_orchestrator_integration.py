"""Integration of Multi-Agent Orchestrator with facebook_publisher.py.

This module connects the orchestrator with the Facebook publisher workflow,
enabling task delegation to specialized agents for content generation,
code debugging, and data checking.
"""

import asyncio
import sys
import os

# Add the multi-agent orchestrator to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_orchestrator._base import Orchestrator
from multi_agent_orchestrator._content_agent import ContentAgent
from multi_agent_orchestrator._code_debug_agent import CodeDebugAgent
from multi_agent_orchestrator._data_agent import DataAgent
from multi_agent_orchestrator._integration import ScriptIntegration


class FacebookPublisherIntegration:
    """Integration layer for Facebook publisher with agent orchestration."""
    
    def __init__(self):
        self.orchestrator = Orchestrator("FacebookPublisher")
        self._setup_agents()
        self.integration = ScriptIntegration(self.orchestrator)
    
    def _setup_agents(self):
        """Register all specialized agents."""
        content_agent = ContentAgent()
        code_agent = CodeDebugAgent()
        data_agent = DataAgent()
        
        self.orchestrator.register_agent(content_agent)
        self.orchestrator.register_agent(code_agent)
        self.orchestrator.register_agent(data_agent)
    
    async def process_post_with_orchestrator(self, message: str) -> dict:
        """Process a Facebook post through the full orchestrator pipeline."""
        # Step 1: Content generation agent enhances the post
        content_task = {
            "type": "post_generation",
            "content_type": "post",
            "prompt": message,
            "style": "engaging",
            "target": "facebook",
        }
        content_result = await self.orchestrator.delegate(content_task)
        
        # Step 2: Validate the generated content
        if content_result.get("status") == "completed":
            enhanced_content = content_result.get("generated_content", message)
        else:
            enhanced_content = message
        
        # Step 3: Check database state for any related data
        db_task = {"type": "check_database", "query_type": "check_database"}
        db_result = await self.orchestrator.delegate(db_task)
        
        # Step 4: Return comprehensive result
        return {
            "original_message": message,
            "enhanced_content": enhanced_content,
            "content_agent_result": content_result,
            "database_status": db_result.get("data", {}).get("status", "unknown"),
            "overall_status": "completed" if content_result.get("status") == "completed" else "error",
        }
    
    async def debug_publisher_code(self, script_code: str) -> dict:
        """Debug Facebook publisher code through the code agent."""
        task = {
            "type": "fix_indentation",
            "code": script_code,
            "language": "python",
        }
        result = await self.orchestrator.delegate(task)
        return result
    
    async def check_system_health(self) -> dict:
        """Check overall system health through data agent."""
        task = {"type": "check_database", "query_type": "check_database"}
        result = await self.orchestrator.delegate(task)
        
        # Also check code health by debugging the publisher
        code_task = {"type": "fix_indentation", "code": "body_lower = \"\"\n    try:", "language": "python"}
        code_result = await self.orchestrator.delegate(code_task)
        
        return {
            "database_status": result.get("data", {}).get("status", "unknown"),
            "code_healthy": code_result.get("status") == "completed",
            "system_health": "healthy" if (result.get("data", {}).get("status") == "connected" and code_result.get("status") == "completed") else "needs_attention",
        }
    
    async def execute_concurrent_workflow(self, tasks: list) -> list:
        """Execute multiple workflow tasks concurrently."""
        return await self.orchestrator.execute_concurrent(tasks)


# Example usage
async def main():
    """Example integration usage."""
    integration = FacebookPublisherIntegration()
    
    print("=" * 60)
    print("Facebook Publisher + Orchestrator Integration")
    print("=" * 60)
    
    # 1. Process a post
    print("\n1. Processing Facebook post...")
    result = await integration.process_post_with_orchestrator(
        "Check out our new AI features! 🚀"
    )
    print(f"   Original: {result['original_message']}")
    print(f"   Enhanced: {result['enhanced_content']}")
    print(f"   Content Status: {result['content_agent_result'].get('status')}")
    print(f"   DB Status: {result['database_status']}")
    
    # 2. Debug code
    print("\n2. Debugging publisher code...")
    buggy_code = "body_lower = \"\"\n    try:"
    debug_result = await integration.debug_publisher_code(buggy_code)
    print(f"   Fixed code: {debug_result.get('fixed_code', 'N/A')}")
    
    # 3. System health check
    print("\n3. System health check...")
    health = await integration.check_system_health()
    print(f"   Database: {health['database_status']}")
    print(f"   Code health: {'Good' if health['code_healthy'] else 'Issues found'}")
    print(f"   Overall: {health['system_health']}")
    
    # 4. Concurrent execution
    print("\n4. Concurrent workflow execution...")
    concurrent_tasks = [
        {"type": "post_generation", "prompt": "Tip 1", "content_type": "caption"},
        {"type": "fix_indentation", "code": "x = 1", "language": "python"},
    ]
    concurrent_results = await integration.execute_concurrent_workflow(concurrent_tasks)
    print(f"   Completed {len(concurrent_results)} tasks concurrently")
    
    print("\n" + "=" * 60)
    print("Integration demo complete!")


if __name__ == "__main__":
    asyncio.run(main())