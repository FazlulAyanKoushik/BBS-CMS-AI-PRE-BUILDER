"""Contracts package for BBS-CMS AI Pre-Builder.

This package contains the formal contracts (interfaces) between AI agents.
The primary contract is SiteSpec, which defines the website structure
specification passed from AI_AGENT_1 to AI_AGENT_2.
"""

from app.contracts.version import CONTRACT_VERSION, SUPPORTED_VERSIONS, AGENT1_VERSION, AGENT2_VERSION

__all__ = [
    "CONTRACT_VERSION",
    "SUPPORTED_VERSIONS",
    "AGENT1_VERSION",
    "AGENT2_VERSION",
]

# SiteSpec can be imported directly from app.contracts.site_spec when needed
# to avoid circular imports