"""Demo script for the Multi-Agent Orchestrator."""

import sys
import os

# Add the workspace to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_orchestrator._base import Orchestrator, BaseAgent
from multi_agent_orchestrator._content_agent import ContentAgent
from multi_agent_orchestrator._code_debug_agent import CodeDebugAgent
from multi_agent_orchestrator._data_agent import DataAgent
from multi_agent_orchestrator._integration import ScriptIntegration


async def demo_orchestrator():
    """Demonstrate the orchestrator with multiple agents."""
    # Initialize orchestrator
    orch = Orchestrator("MainOrch")

    # Register specialized agents
    content_agent = ContentAgent()
    code_agent = CodeDebugAgent()
    data_agent = DataAgent()

    orch.register_agent(content_agent)
    orch.register_agent(code_agent)
    orch.register_agent(data_agent)

    # Example 1: Content generation
    print("=" * 60)
    print("Example 1: Content Generation")
    print("=" * 60)
    task1 = {"type": "post_generation", "prompt": "New AI features update", "content_type": "post"}
    result1 = await orch.delegate(task1)
    print(f"Generated: {result1.get('generated_content', 'N/A')}\n")

    # Example 2: Code debugging
    print("=" * 60)
    print("Example 2: Code Debugging")
    print("=" * 60)
    buggy_code = "body_lower = \"\"\n    try:"
    task2 = {"type": "fix_indentation", "code": buggy_code, "language": "python"}
    result2 = await orch.delegate(task2)
    print(f"Fixed code: {result2.get('fixed_code', 'N/A')}\n")

    # Example 3: Data check
    print("=" * 60)
    print("Example 3: Data State Check")
    print("=" * 60)
    task3 = {"type": "check_database", "query_type": "check_database"}
    result3 = await orch.delegate(task3)
    print(f"Database status: {result3.get('data', {}).get('status', 'N/A')}\n")

    # Example 4: Concurrent execution
    print("=" * 60)
    print("Example 4: Concurrent Task Execution")
    print("=" * 60)
    concurrent_tasks = [
        {"type": "post_generation", "prompt": "Tip 1", "content_type": "caption"},
        {"type": "fix_indentation", "code": "x = 1", "language": "python"},
        {"type": "check_database", "query_type": "check_database"},
    ]
    results = await orch.execute_concurrent(concurrent_tasks)
    print(f"Completed {len(results)} concurrent tasks\n")

    # Print agent stats
    print("=" * 60)
    print("Agent Statistics")
    print("=" * 60)
    stats = orch.get_agent_stats()
    for agent_id, stat in stats.items():
        print(f"{stat['name']}: {stat['success_count']}/{stat['execution_count']} successs "
              f"({stat['success_rate']*100:.1f}%)")

    print("\n" + "=" * 60)
    print("Orchestrator demo complete!")
    print("=" * 60)


async def demo_integration():
    """Demonstrate integration with existing scripts."""
    print("\n" + "=" * 60)
    print("Integration Demo")
    print("=" * 60)

    orch = Orchestrator("IntegrationOrch")
    content_agent = ContentAgent()
    code_agent = CodeDebugAgent()
    data_agent = DataAgent()

    orch.register_agent(content_agent)
    orch.register_agent(code_agent)
    orch.register_agent(data_agent)

    integration = ScriptIntegration(orch)

    # Facebook post processing
    print("\n1. Facebook Post Processing:")
    fb_result = await integration.process_facebook_post("Check out our new features!")
    print(f"   Status: {fb_result.get('status')}")
    print(f"   Content: {fb_result.get('generated_content', 'N/A')[:50]}...\n")

    # Script debugging
    print("2. Script Debugging:")
    buggy = "body_lower = \"\"\n    try:"
    debug_result = await integration.debug_script(buggy)
    print(f"   Fixed: {debug_result.get('fixed_code', 'N/A')}\n")

    # Database check
    print("3. Database State Check:")
    db_result = await integration.check_database_state()
    print(f"   Status: {db_result.get('data', {}).get('status', 'N/A')}\n")

    # Concurrent processing
    print("4. Concurrent Task Processing:")
    tasks = [
        {"type": "post_generation", "prompt": "Tip A", "content_type": "caption"},
        {"type": "fix_indentation", "code": "y = 2", "language": "python"},
        {"type": "check_database", "query_type": "check_database"},
    ]
    concurrent_results = await integration.concurrent_task_processing(tasks)
    print(f"   Completed {len(concurrent_results)} tasks\n")

    print("=" * 60)


if __name__ == "__main__":
    print("Running Orchestrator Demo...")
    asyncio_run_result = __import__('asyncio').run(demo_orchestrator())
    print("\nRunning Integration Demo...")
    asyncio.run(demo_integration())
    print("\nAll demos complete!")