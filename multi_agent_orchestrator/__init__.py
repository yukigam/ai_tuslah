"""Multi-Agent Orchestrator Package.

Manages specialized agents for task delegation and concurrent execution.
"""

import sys
import os

# Add the parent directory to path so we can import the submodules
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from multi_agent_orchestrator._base import BaseAgent
from multi_agent_orchestrator._orchestrator import Orchestrator
from multi_agent_orchestrator._content_agent import ContentAgent
from multi_agent_orchestrator._code_debug_agent import CodeDebugAgent
from multi_agent_orchestrator._data_agent import DataAgent

__all__ = [
    'BaseAgent',
    'Orchestrator',
    'ContentAgent',
    'CodeDebugAgent',
    'DataAgent',
]