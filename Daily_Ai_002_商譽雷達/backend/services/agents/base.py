from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import json


class BaseAgent:
    """Base AI Agent with common capabilities for Sentinel AI ECXIP."""

    def __init__(self, name: str, description: str, model_tier: str = "PRO"):
        self.name = name
        self.description = description
        self.model_tier = model_tier
        self.memory: List[Dict] = []
        self.knowledge: Dict[str, Any] = {}
        self.tools: List[Callable] = []
        self.call_count = 0
        self.last_called: Optional[datetime] = None

    async def analyze(self, context: Dict) -> Dict:
        """Analyze context and return insights."""
        raise NotImplementedError

    async def recommend(self, analysis: Dict) -> List[Dict]:
        """Generate recommendations from analysis."""
        raise NotImplementedError

    def remember(self, key: str, value: Any):
        """Store in agent memory."""
        self.memory.append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

    def recall(self, key: str) -> Optional[Any]:
        """Recall from agent memory."""
        for m in reversed(self.memory):
            if m["key"] == key:
                return m["value"]
        return None

    def recall_all(self, key: str) -> List[Dict]:
        """Recall all matching memories."""
        return [m for m in self.memory if m["key"] == key]

    def forget(self, key: str):
        """Remove all memories with given key."""
        self.memory = [m for m in self.memory if m["key"] != key]

    def clear_memory(self):
        """Clear all agent memory."""
        self.memory.clear()

    def register_tool(self, tool: Callable):
        """Register a callable tool."""
        self.tools.append(tool)

    def use_tool(self, tool_name: str, *args, **kwargs) -> Optional[Any]:
        """Execute a registered tool by name."""
        for tool in self.tools:
            if getattr(tool, "__name__", "") == tool_name:
                return tool(*args, **kwargs)
        return None

    def log_call(self):
        """Log an agent invocation."""
        self.call_count += 1
        self.last_called = datetime.now()

    def to_dict(self) -> Dict:
        """Serialize agent metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "model_tier": self.model_tier,
            "call_count": self.call_count,
            "last_called": self.last_called.isoformat() if self.last_called else None,
            "memory_size": len(self.memory),
            "tools_count": len(self.tools),
        }

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        caps = []
        for attr_name in dir(self):
            if not attr_name.startswith("_"):
                attr = getattr(self, attr_name)
                if callable(attr) and attr_name not in ("to_dict", "get_capabilities", "remember", "recall",
                                                         "recall_all", "forget", "clear_memory", "register_tool",
                                                         "use_tool", "log_call"):
                    caps.append(attr_name)
        return caps
