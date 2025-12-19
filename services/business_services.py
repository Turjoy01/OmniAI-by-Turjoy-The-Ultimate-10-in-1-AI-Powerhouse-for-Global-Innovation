"""
Business AI Services

All business-related services as classes.
Each service uses the unified OpenAIService.
"""

import json
from .openai_service import OpenAIService


class AdsService:
    """Service for generating advertisements"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def generate_ad(
        self,
        product_name: str,
        target_audience: str,
        ad_type: str,
        key_features: list = None,
        tone: str = "professional"
    ):
        """Generate AI-powered advertisement content"""
        features_text = "\n".join(key_features) if key_features else "N/A"
        
        prompt = f"""Create a compelling {ad_type} ad for:
Product: {product_name}
Target Audience: {target_audience}
Tone: {tone}
Key Features: {features_text}

Generate:
1. Headline (attention-grabbing)
2. Ad Copy (persuasive description)
3. Call-to-Action (clear and actionable)
4. Hashtags (if applicable for social media)

Format the output in a structured way."""
        
        return await self.openai_service.generate_completion(
            prompt,
            system_message="You are a professional business AI assistant specializing in marketing and advertising."
        )


class InvoiceService:
    """Service for generating invoices"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def generate_invoice(
        self,
        company_name: str,
        client_name: str,
        client_email: str,
        items: list,
        tax_rate: float = 0.0,
        notes: str = None
    ):
        """Generate professional invoice with automatic calculations"""
        items_json = json.dumps(items, indent=2)
        
        prompt = f"""Generate a professional invoice with the following details:

Company: {company_name}
Client: {client_name}
Client Email: {client_email}
Tax Rate: {tax_rate}%
Additional Notes: {notes or 'None'}

Items:
{items_json}

Create a detailed invoice including:
1. Invoice number (generate a realistic one)
2. Date (today's date)
3. Itemized list with calculations
4. Subtotal
5. Tax calculation
6. Total amount
7. Payment terms
8. Professional formatting

Output in a clear, structured format."""
        
        return await self.openai_service.generate_completion(
            prompt,
            system_message="You are a professional business AI assistant specializing in financial documents."
        )


class EmailService:
    """Service for generating business emails"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def generate_email(
        self,
        email_type: str,
        subject: str,
        key_points: list,
        recipient_name: str = None,
        tone: str = "professional"
    ):
        """Generate professional emails for various purposes"""
        points_text = "\n".join([f"- {point}" for point in key_points])
        recipient = recipient_name if recipient_name else "[Recipient Name]"
        
        prompt = f"""Write a {tone} {email_type} email with:

Recipient: {recipient}
Subject: {subject}
Tone: {tone}

Key Points to Cover:
{points_text}

Generate a complete email including:
1. Subject line (if different from provided)
2. Greeting
3. Body paragraphs
4. Call-to-action
5. Professional closing

Make it natural and engaging."""
        
        return await self.openai_service.generate_completion(
            prompt,
            system_message="You are a professional business AI assistant specializing in business communication."
        )


class CRMService:
    """Service for CRM-related tasks"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def process_crm_task(self, task: str, customer_data: dict):
        """Process CRM tasks with AI analysis"""
        customer_json = json.dumps(customer_data, indent=2)
        
        task_prompts = {
            "lead_summary": f"""Analyze this lead and create a comprehensive summary:
{customer_json}

Provide:
1. Lead Quality Score (1-10)
2. Key Insights
3. Recommended Actions
4. Priority Level
5. Next Steps""",
            
            "follow_up_schedule": f"""Create a follow-up schedule for this customer:
{customer_json}

Generate:
1. Immediate follow-up (24 hours)
2. Short-term follow-ups (1 week)
3. Long-term nurturing plan
4. Recommended communication channels
5. Key talking points for each touchpoint""",
            
            "customer_analysis": f"""Perform detailed customer analysis:
{customer_json}

Analyze:
1. Customer Profile
2. Behavior Patterns
3. Purchase Potential
4. Pain Points
5. Personalized Recommendations"""
        }
        
        prompt = task_prompts.get(
            task,
            f"Process this CRM task '{task}' with data: {customer_json}"
        )
        
        return await self.openai_service.generate_completion(
            prompt,
            system_message="You are a professional business AI assistant specializing in customer relationship management."
        )


class MenuService:
    """Service for generating restaurant menus"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def generate_menu(
        self,
        restaurant_type: str,
        cuisine: str,
        items_count: int = 10,
        price_range: str = "medium"
    ):
        """Generate restaurant menu with items and pricing"""
        prompt = f"""Create a professional restaurant menu for:

Restaurant Type: {restaurant_type}
Cuisine: {cuisine}
Number of Items: {items_count}
Price Range: {price_range}

Generate a complete menu with:
1. Creative dish names
2. Appetizing descriptions
3. Realistic prices (in USD)
4. Categorized sections (appetizers, mains, desserts, drinks)
5. Dietary information (vegetarian, vegan, gluten-free markers)

Make it appealing and professional."""
        
        return await self.openai_service.generate_completion(
            prompt,
            max_tokens=3000,
            system_message="You are a professional business AI assistant specializing in restaurant and hospitality."
        )


class SEOService:
    """Service for generating SEO content"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def generate_seo_content(
        self,
        target_keyword: str,
        content_type: str,
        word_count: int = 500,
        include_meta: bool = True
    ):
        """Generate SEO-optimized content with meta tags"""
        prompt = f"""Create SEO-optimized content:

Target Keyword: {target_keyword}
Content Type: {content_type}
Word Count: ~{word_count} words

Generate:
1. SEO-optimized title (with keyword)
2. Main content (naturally incorporate keyword)
3. Subheadings (H2, H3 with variations)
4. Internal linking suggestions
"""
        
        if include_meta:
            prompt += """5. Meta Title (55-60 characters)
6. Meta Description (150-160 characters)
7. Focus Keywords (primary and secondary)
8. URL slug suggestion"""
        
        return await self.openai_service.generate_completion(
            prompt,
            max_tokens=2500,
            system_message="You are a professional business AI assistant specializing in SEO and content marketing."
        )


class ProductService:
    """Service for generating product descriptions"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def generate_product_description(
        self,
        product_name: str,
        category: str,
        features: list,
        target_audience: str,
        tone: str = "persuasive",
        length: str = "medium"
    ):
        """Generate compelling product descriptions"""
        features_text = "\n".join([f"- {feature}" for feature in features])
        
        length_words = {"short": 100, "medium": 250, "long": 500}
        word_target = length_words.get(length, 250)
        
        prompt = f"""Write a compelling product description for:

Product: {product_name}
Category: {category}
Target Audience: {target_audience}
Tone: {tone}
Length: ~{word_target} words

Features:
{features_text}

Create:
1. Attention-grabbing headline
2. Engaging product description
3. Benefits-focused content (not just features)
4. Social proof elements
5. Strong call-to-action
6. SEO-friendly keywords

Make it persuasive and conversion-focused."""
        
        return await self.openai_service.generate_completion(
            prompt,
            max_tokens=2000,
            system_message="You are a professional business AI assistant specializing in e-commerce and product marketing."
        )