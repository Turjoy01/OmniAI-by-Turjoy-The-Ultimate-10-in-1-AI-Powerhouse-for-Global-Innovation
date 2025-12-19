"""
AI Agents Marketplace Service

Provides tailored suggestions for different agent types
within the AI Agents Marketplace using OpenAI.
"""

import re
from typing import Callable, Dict, List, Optional

from models.requests import AgentTypeEnum
from .openai_service import OpenAIService
from utils.prompts import AgentPrompts


class AgentsService:
    """
    Service responsible for generating agent-specific suggestions using OpenAI.
    Each agent focuses on recommendations rather than automated actions.
    """

    def __init__(self) -> None:
        self.openai_service = OpenAIService()
        self._strategies: Dict[AgentTypeEnum, Callable[[Optional[str]], str]] = {
            AgentTypeEnum.MARKETING: AgentPrompts.marketing_agent,
            AgentTypeEnum.RESTAURANT: AgentPrompts.restaurant_agent,
            AgentTypeEnum.REAL_ESTATE: AgentPrompts.real_estate_agent,
            AgentTypeEnum.LEGAL: AgentPrompts.legal_agent,
            AgentTypeEnum.TEACHER: AgentPrompts.teacher_agent,
            AgentTypeEnum.FITNESS: AgentPrompts.fitness_agent,
            AgentTypeEnum.BUSINESS_PLAN_BUILDER: AgentPrompts.business_plan_builder_agent,
            AgentTypeEnum.FINANCIAL_FORECASTS: AgentPrompts.financial_forecasts_agent,
            AgentTypeEnum.INDUSTRY_RESEARCH: AgentPrompts.industry_research_agent,
            AgentTypeEnum.LIVEPLAN_ASSISTANT: AgentPrompts.liveplan_assistant_agent,
        }

    async def get_suggestions(
        self, agent_type: AgentTypeEnum, user_input: Optional[str] = None
    ) -> List[str]:
        """
        Return tailored suggestions for the selected agent type using OpenAI.

        Args:
            agent_type: Selected agent enum
            user_input: Optional context shared by the user
            
        Returns:
            List of suggestion strings
        """
        prompt_generator = self._strategies.get(agent_type)
        if not prompt_generator:
            raise ValueError(f"Unsupported agent type: {agent_type}")
        
        prompt = prompt_generator(user_input)
        
        system_message = f"You are an expert AI assistant specialized in providing actionable, professional suggestions."
        
        response = await self.openai_service.generate_completion(
            prompt,
            system_message=system_message
        )
        
        # Parse the response into a list of suggestions
        suggestions = self._parse_suggestions(response)
        return suggestions
    
    @staticmethod
    def _parse_suggestions(response: str) -> List[str]:
        """
        Parse the AI response into a list of suggestions.
        Handles various formats: numbered lists, bullet points, etc.
        """
        suggestions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line = re.sub(r'^\d+[\.\)]\s*', '', line)  # Remove "1. " or "1) "
            line = re.sub(r'^[-*•]\s*', '', line)  # Remove "- " or "* " or "• "
            line = line.strip()
            
            if line and len(line) > 10:  # Only add substantial suggestions
                suggestions.append(line)
        
        # If we got fewer than 4 suggestions, try to split longer ones
        if len(suggestions) < 4 and suggestions:
            # Sometimes AI returns fewer but longer suggestions
            # Return what we have (minimum 1, up to 4)
            return suggestions[:4] if len(suggestions) >= 4 else suggestions
        
        # Ensure we return at least 1 suggestion, max 4
        return suggestions[:4] if suggestions else [response.strip()]

