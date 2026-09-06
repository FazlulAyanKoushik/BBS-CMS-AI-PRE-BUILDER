"""Agent Registry for BBS-CMS AI Pre-Builder.

Provides a central registry for discovering and instantiating AI agents.
Supports multiple agents (Agent 1, Agent 2, etc.) with clean separation.
"""

from __future__ import annotations

from typing import Any

from app.agents.agent1 import AIAgent1, AGENT_NAME as AGENT1_NAME
from app.agents.agent2 import AIAgent2, AGENT_NAME as AGENT2_NAME


class AgentRegistry:
    """Registry for managing AI agents."""
    
    def __init__(self) -> None:
        self._agents: dict[str, Any] = {}
        self._register_default_agents()
    
    def _register_default_agents(self) -> None:
        """Register the default agents."""
        self._agents[AGENT1_NAME] = AIAgent1
        self._agents[AGENT2_NAME] = AIAgent2
    
    def get_agent_class(self, agent_name: str) -> type | None:
        """Get an agent class by name."""
        return self._agents.get(agent_name)
    
    def create_agent(self, agent_name: str, **kwargs) -> Any:
        """Create an agent instance by name."""
        agent_class = self.get_agent_class(agent_name)
        if agent_class is None:
            raise ValueError(f"Unknown agent: {agent_name}")
        return agent_class(**kwargs)
    
    def list_agents(self) -> list[str]:
        """List all registered agent names."""
        return list(self._agents.keys())
    
    def register_agent(self, agent_name: str, agent_class: type) -> None:
        """Register a new agent class."""
        self._agents[agent_name] = agent_class


# Global registry instance
registry = AgentRegistry()


def get_agent(agent_name: str, **kwargs) -> Any:
    """Convenience function to get an agent instance from the global registry."""
    return registry.create_agent(agent_name, **kwargs)


def list_available_agents() -> list[str]:
    """List all available agents."""
    return registry.list_agents()