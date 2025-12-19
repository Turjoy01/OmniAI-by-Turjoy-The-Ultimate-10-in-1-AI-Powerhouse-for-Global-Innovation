"""
AI prompt templates for platform-agnostic social media content generation and AI agents marketplace.
"""

from typing import Optional


def _platform_label(platform: str) -> str:
    """Normalize the platform label for prompts."""
    return platform.strip() or "the target platform"


class GlobalPrompts:
    """Prompt templates that adapt to any social platform."""
    
    @staticmethod
    def caption(platform: str, topic: str, tone: str = "casual", length: str = "medium") -> str:
        normalized_platform = _platform_label(platform)
        return f"""Generate an engaging caption for {normalized_platform} about: {topic}

Requirements:
- Platform-specific nuances for {normalized_platform}
- Tone: {tone}
- Length: {length} (short: 1-2 sentences, medium: 3-5 sentences, long: 6-10 sentences)
- Use formatting, emojis, or mentions that fit {normalized_platform}
- Add a call-to-action that suits {normalized_platform} culture

Respond with the caption only."""
    
    @staticmethod
    def hashtags(platform: str, topic: str, count: int = 10) -> str:
        normalized_platform = _platform_label(platform)
        return f"""Generate {count} relevant hashtags for {normalized_platform} about: {topic}

Requirements:
- Include a mix of broad and niche tags suitable for {normalized_platform}
- Reflect current trends and community language
- Format: one hashtag per line (include # if the platform uses it)

Respond with hashtags only."""
    
    @staticmethod
    def content_ideas(platform: str, niche: str, count: int = 5) -> str:
        normalized_platform = _platform_label(platform)
        return f"""Generate {count} creative content ideas for {normalized_platform} in the niche: {niche}

Requirements:
- Mix of popular and emerging content formats for {normalized_platform}
- Provide a short description for each idea
- Highlight hooks, calls-to-action, or storytelling angles that resonate on {normalized_platform}

Format:
[Format] - [Idea Title]: [Brief Description]"""
    
    @staticmethod
    def video_title(platform: str, topic: str, style: str = "clickable") -> str:
        normalized_platform = _platform_label(platform)
        return f"""Generate a compelling {normalized_platform} video title about: {topic}

Requirements:
- Style: {style} (clickable, informative, educational, entertaining, inspirational, etc.)
- Optimize for search and click-through on {normalized_platform}
- Keep under 70 characters when possible
- Avoid clickbait wording

Respond with the title only."""
    
    @staticmethod
    def video_description(platform: str, topic: str, length: str = "medium") -> str:
        normalized_platform = _platform_label(platform)
        return f"""Write a {length} {normalized_platform} video description about: {topic}

Requirements:
- Include a strong hook in the first sentence
- Add relevant keywords and optional timestamps
- Close with a call-to-action that fits {normalized_platform}
- Keep formatting clean and readable

Respond with the description only."""
    
    @staticmethod
    def video_tags(platform: str, topic: str, count: int = 15) -> str:
        normalized_platform = _platform_label(platform)
        return f"""Generate {count} SEO-friendly tags/keywords for a {normalized_platform} video about: {topic}

Requirements:
- Mix of short-tail and long-tail keywords
- Reflect search intent on {normalized_platform}
- Format: one tag per line (no # symbol unless common on the platform)

Respond with tags only."""


class AgentPrompts:
    """Prompt templates for AI Agents Marketplace suggestions."""
    
    @staticmethod
    def marketing_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "general marketing strategy"
        return f"""You are an expert Marketing Agent. Provide 4 tailored, actionable marketing suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on modern marketing strategies and best practices
- Consider digital marketing channels, content strategy, and audience engagement
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def restaurant_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "restaurant operations"
        return f"""You are an expert Restaurant Agent. Provide 4 tailored, actionable restaurant management suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on menu optimization, customer experience, operations, and marketing
- Consider food trends, service quality, and profitability
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def real_estate_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "real estate business"
        return f"""You are an expert Real Estate Agent. Provide 4 tailored, actionable real estate suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on property marketing, client relations, market analysis, and sales strategies
- Consider current market trends and best practices
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def legal_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "legal practice"
        return f"""You are an expert Legal Agent. Provide 4 tailored, actionable legal practice suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on client communication, case management, legal documentation, and practice growth
- Consider legal ethics and professional standards
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def teacher_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "teaching and education"
        return f"""You are an expert Teacher Agent. Provide 4 tailored, actionable teaching suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on lesson planning, student engagement, assessment strategies, and educational best practices
- Consider different learning styles and modern teaching methods
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def fitness_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "fitness and wellness"
        return f"""You are an expert Fitness Agent. Provide 4 tailored, actionable fitness and wellness suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on workout planning, nutrition, recovery, and goal achievement
- Consider different fitness levels and health considerations
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def business_plan_builder_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "business planning"
        return f"""You are an expert Business Plan Builder Agent. Provide 4 tailored, actionable business plan suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on business structure, market analysis, financial planning, and strategic planning
- Consider industry best practices and investor expectations
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def financial_forecasts_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "financial forecasting"
        return f"""You are an expert Financial Forecasts & Scenarios Agent. Provide 4 tailored, actionable financial forecasting suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on financial modeling, scenario planning, risk analysis, and cash flow management
- Consider different business scenarios and financial metrics
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def industry_research_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "industry research"
        return f"""You are an expert Industry Research Agent. Provide 4 tailored, actionable industry research suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on market analysis, competitive intelligence, trend identification, and industry insights
- Consider data sources, research methodologies, and strategic implications
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
    
    @staticmethod
    def liveplan_assistant_agent(user_input: Optional[str] = None) -> str:
        context = user_input or "business plan development"
        return f"""You are an expert AI-Powered LivePlan Assistant. Provide 4 tailored, actionable LivePlan suggestions based on: {context}

Requirements:
- Each suggestion should be specific, actionable, and practical
- Focus on business plan structure, financial projections, presentation quality, and investor readiness
- Consider LivePlan best practices and professional business plan standards
- Make suggestions relevant to the user's context

Format your response as a numbered list (1-4), with each suggestion on a new line. Be concise but informative."""
