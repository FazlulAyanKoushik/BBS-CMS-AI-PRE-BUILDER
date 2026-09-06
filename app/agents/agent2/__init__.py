"""AI Agent 2 package (Future Implementation).

This package will contain AI_AGENT_2 which consumes the SiteSpec
from AI_AGENT_1 and generates dynamic website content.
"""

from app.agents.agent2.agent import AIAgent2, BaseContentGenerator, get_agent2

__all__ = ["AIAgent2", "BaseContentGenerator", "get_agent2"]