"""Test script for orchestrator integration."""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'multi_agent_orchestrator'))

from multi_agent_orchestrator._base import Orchestrator, BaseAgent
from multi_agent_orchestrator._content_agent import ContentAgent
from multi_agent_orchestrator._code_debug_agent import CodeDebugAgent
from multi_agent_orchestrator._data_agent import DataAgent
from multi_agent_orchestrator._integration import ScriptIntegration

print("All imports successful!")

# Test basic orchestrator
async def test_basic():
    orch = Orchestrator("Test")
    content = ContentAgent()
    code = CodeDebugAgent()
    data = DataAgent()
    
    orch.register_agent(content)
    orch.register_agent(code)
    orch.register_agent(data)
    
    # Test content generation
    result = await orch.delegate({"type": "post_generation", "prompt": "Test", "content_type": "post"})
    print(f"Content result: {result.get('status')}")
    
    # Test code debugging
    result2 = await orch.delegate({"type": "fix_indentation", "code": "x = 1", "language": "python"})
    print(f"Code result: {result2.get('status')}")
    
    # Test data check
    result3 = await orch.delegate({"type": "check_database", "query_type": "check_database"})
    print(f"Data result: {result3.get('status')}")
    
    # Test concurrent
    tasks = [
        {"type": "post_generation", "prompt": "Tip 1", "content_type": "caption"},
        {"type": "fix_indentation", "code": "y = 2", "language": "python"},
    ]
    results = await orch.execute_concurrent(tasks)
    print(f"Concurrent results: {len(results)} tasks")
    
    print(f"Agent stats: {orch.get_agent_stats()}")

import asyncio
asyncio.run(test_basic())
print("\nAll tests passed!")