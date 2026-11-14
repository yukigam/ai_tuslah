"""Core integration logic between Telegram and Orchestrator."""

import asyncio
from typing import Dict, Optional, Tuple

from multi_agent_orchestrator._base import Orchestrator
from multi_agent_orchestrator._content_agent import ContentAgent
from multi_agent_orchestrator._code_debug_agent import CodeDebugAgent
from multi_agent_orchestrator._data_agent import DataAgent
from multi_agent_orchestrator._integration import ScriptIntegration


class TelegramOrchestratorIntegration:
    """Integration layer between Telegram Bot and Multi-Agent Orchestrator."""
    
    def __init__(self, orchestrator: Optional[Orchestrator] = None):
        if orchestrator is None:
            self.orchestrator = Orchestrator("TelegramBotOrchestrator")
            self._register_default_agents()
        else:
            self.orchestrator = orchestrator
        
        self.integration = ScriptIntegration(self.orchestrator)
    
    def _register_default_agents(self):
        """Register all default specialized agents."""
        content_agent = ContentAgent()
        code_agent = CodeDebugAgent()
        data_agent = DataAgent()
        
        self.orchestrator.register_agent(content_agent)
        self.orchestrator.register_agent(code_agent)
        self.orchestrator.register_agent(data_agent)
    
    async def handle_message(self, user_id: int, user_message: str, 
                           chat_id: int) -> str:
        """Handle incoming Telegram message through Orchestrator."""
        task_type = self._classify_message(user_message)
        task = self._create_task(user_message, task_type)
        result = await self.orchestrator.delegate(task)
        return self._format_telegram_response(result, user_message)
    
    @staticmethod
    def _classify_message(message: str) -> str:
        """Classify message to determine task type."""
        message_lower = message.lower().strip()
        
        content_keywords = ['post', 'content', 'write', 'generate', 'create',
                           'caption', 'article', 'blog', 'status']
        if any(kw in message_lower for kw in content_keywords):
            return "post_generation"
        
        code_keywords = ['code', 'bug', 'error', 'fix', 'indent', 'python',
                        'debug', 'script', 'program']
        if any(kw in message_lower for kw in code_keywords):
            return "fix_indentation"
        
        data_keywords = ['database', 'query', 'check', 'data', 'supabase',
                        'records', 'table', 'status']
        if any(kw in message_lower for kw in data_keywords):
            return "check_database"
        
        return "post_generation"
    
    @staticmethod
    def _create_task(user_message: str, task_type: str) -> Dict[str, Any]:
        """Create task dictionary for orchestrator."""
        base_task = {
            "id": f"telegram-{int(asyncio.get_event_loop().time())}",
            "timestamp": asyncio.get_event_loop().time(),
        }
        
        if task_type == "post_generation":
            base_task.update({
                "type": "post_generation",
                "content_type": "post",
                "prompt": user_message,
                "style": "professional",
                "target": "telegram",
            })
        elif task_type == "fix_indentation":
            base_task.update({
                "type": "fix_indentation",
                "code": user_message,
                "language": "python",
            })
        elif task_type == "check_database":
            base_task.update({
                "type": "check_database",
                "query_type": "check_database",
            })
        else:
            base_task.update({
                "type": "post_generation",
                "content_type": "post",
                "prompt": user_message,
                "style": "professional",
                "target": "telegram",
            })
        
        return base_task
    
    @staticmethod
    def _format_telegram_response(result: Dict, original_message: str) -> str:
        """Format orchestrator result for Telegram response."""
        status = result.get("status", "error")
        
        if status == "completed":
            content_type = result.get("content_type", "")
            
            if content_type == "post" and "generated_content" in result:
                content = result["generated_content"]
                return f"✅ *Task Completed*\n\n{content}\n\n*Original request:* {original_message}"
            
            elif "fixed_code" in result:
                code = result["fixed_code"]
                return f"✅ *Code Fixed*\n\n```python\n{code}\n```\n\n*Original request:* {original_message}"
            
            elif "data" in result:
                data = str(result["data"])
                return f"✅ *Database Check*\n\n```{data}\n```\n\n*Original request:* {original_message}"
            
            else:
                return f"✅ *Completed*\n\n*Result:* {str(result)[:200]}\n\n*Original request:* {original_message}"
        
        elif status == "error":
            error = result.get("error", "Unknown error")
            return f"❌ *Error*\n\n*An error occurred:* {error}\n\n*Original request:* {original_message}"
        
        elif status == "validation_failed":
            error = result.get("error", "Validation failed")
            return f"⚠️ *Validation Failed*\n\n*{error}*\n\n*Original request:* {original_message}"
        
        else:
            return f"⚠️ *Unexpected Response*\n\n*Status:* {status}\n\n*Original request:* {original_message}"