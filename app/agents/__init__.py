"""Agents package for BBS-CMS AI Pre-Builder.

This package contains the AI agents responsible for different stages of
website generation:

- agent1: AI_AGENT_1 - Generates website structure specification (SiteSpec)
  from business profile and user criteria.
- agent2: AI_AGENT_2 - (Future) Generates dynamic website content from SiteSpec.
"""

from app.agents.agent1 import AGENT_NAME, AIAgent1, run_agent

__all__ = ["AGENT_NAME", "AIAgent1", "run_agent"]