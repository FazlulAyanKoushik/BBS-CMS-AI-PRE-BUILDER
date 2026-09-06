"""AI Agent 1: Website Structure Specification Generator.

This module contains AI_AGENT_1 which takes a business profile and user criteria
and returns a structured website specification (SiteSpec) as JSON.
"""

from app.agents.agent1.agent import AGENT_NAME, AIAgent1, run_agent

__all__ = ["AGENT_NAME", "AIAgent1", "run_agent"]