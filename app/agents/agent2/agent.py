"""AI Agent 2: Website Content Generator (Future Implementation).

This module defines the interface for AI_AGENT_2, which will consume the
SiteSpec produced by AI_AGENT_1 and generate dynamic website content
(HTML, CSS, JS, or other output formats).

Currently a placeholder for future implementation by a different team.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.contracts.site_spec import SiteSpec  # The contract between Agent 1 and Agent 2


class BaseContentGenerator(ABC):
    """Abstract base class for content generators (AI Agent 2 implementations)."""
    
    name = "AI_AGENT_2"
    
    @abstractmethod
    def generate(self, site_spec: SiteSpec, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate website content from a SiteSpec.
        
        Args:
            site_spec: The website structure specification from AI_AGENT_1
            options: Optional generation options (theme, framework, etc.)
            
        Returns:
            Dictionary containing generated content (pages, assets, etc.)
        """
        pass
    
    @property
    @abstractmethod
    def supported_output_formats(self) -> list[str]:
        """List of supported output formats (e.g., ['html', 'react', 'vue'])."""
        pass


class AIAgent2(BaseContentGenerator):
    """AI_AGENT_2 - Generates dynamic website content from SiteSpec.
    
    This is a stub implementation. The actual implementation will be
    developed by a separate team.
    """
    
    name = "AI_AGENT_2"
    
    def generate(self, site_spec: SiteSpec, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate website content from SiteSpec.
        
        NOTE: This is a placeholder. Real implementation will:
        1. Parse the SiteSpec pages, sections, and fields
        2. Generate appropriate content for each section
        3. Return structured output (HTML, components, etc.)
        """
        raise NotImplementedError(
            "AI_AGENT_2 is not yet implemented. "
            "This will be developed by a separate team."
        )
    
    @property
    def supported_output_formats(self) -> list[str]:
        return ["html", "json"]


def get_agent2() -> AIAgent2:
    """Factory function to get an AI_AGENT_2 instance."""
    return AIAgent2()