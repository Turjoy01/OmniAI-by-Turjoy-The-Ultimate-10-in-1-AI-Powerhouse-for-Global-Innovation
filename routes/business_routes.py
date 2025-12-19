"""
Business AI Tools Routes

All business-related API endpoints with session management.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import uuid

from models.requests import (
    AdsRequest,
    InvoiceRequest,
    EmailRequest,
    CRMRequest,
    MenuRequest,
    SEORequest,
    ProductDescriptionRequest,
    SessionCreateRequest,
)
from models.responses import (
    APIResponse,
    SessionCreateResponse,
    BusinessSession,
    Interaction,
    GenericSessionHistoryResponse,
)
from services.business_services import (
    AdsService,
    InvoiceService,
    EmailService,
    CRMService,
    MenuService,
    SEOService,
    ProductService,
)
from services.database import database
from services.openai_service import OpenAIService

# Initialize router
business_router = APIRouter(prefix="/api/business", tags=["Business Tools"])

# Initialize services
ads_service = AdsService()
invoice_service = InvoiceService()
email_service = EmailService()
crm_service = CRMService()
menu_service = MenuService()
seo_service = SEOService()
product_service = ProductService()
openai_service = OpenAIService()


# ==================== SESSION MANAGEMENT ENDPOINTS ====================

@business_router.post("/session/create", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_business_session(user_id: str):
    """
    Create a new business session
    
    **Step 1:** Call this endpoint to create a session
    - Provide: user_id
    - Returns: session_id
    
    The session will start with title "New Business Session" - it will be auto-updated 
    after the first interaction based on the business tool used.
    
    Use this session_id for all subsequent business tool requests.
    """
    try:
        collection = database.get_collection_by_name("business_sessions")
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create new session with default title
        business_session = BusinessSession(
            session_id=session_id,
            user_id=user_id,
            title="New Business Session",
            interactions=[]
        )
        
        # Save to MongoDB
        await collection.insert_one(business_session.model_dump())
        
        return SessionCreateResponse(
            session_id=session_id,
            user_id=user_id,
            title=business_session.title,
            message="Business session created successfully",
            created_at=business_session.created_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create business session: {str(e)}"
        )

# ==================== HELPER FUNCTION ====================

async def save_business_interaction(
    user_id: str,
    session_id: str,
    request_data: dict,
    response_data: dict,
    tool_name: str
):
    """
    Save a business interaction to the session and generate title if first interaction
    
    Args:
        user_id: User ID
        session_id: Session ID
        request_data: Request data dictionary
        response_data: Response data dictionary
        tool_name: Name of the business tool used
    """
    collection = database.get_collection_by_name("business_sessions")
    
    # Find session
    session = await collection.find_one({
        "session_id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business session not found or does not belong to user"
        )
    
    business_session = BusinessSession(**session)
    
    # Check if this is the first interaction (for title generation)
    is_first_interaction = len(business_session.interactions) == 0
    
    # Generate title from first interaction
    if is_first_interaction:
        try:
            # Create a descriptive prompt based on the tool and request
            title_prompt = f"{tool_name}: {str(request_data)[:100]}"
            generated_title = await openai_service.generate_title(title_prompt)
            business_session.title = generated_title
        except Exception as e:
            # Fallback title if generation fails
            business_session.title = f"{tool_name} Session"
    
    # Create interaction
    interaction = Interaction(
        request=request_data,
        response=response_data,
        timestamp=datetime.utcnow()
    )
    
    # Add interaction to session
    business_session.interactions.append(interaction)
    business_session.updated_at = datetime.utcnow()
    
    # Save to MongoDB
    await collection.update_one(
        {"session_id": session_id, "user_id": user_id},
        {"$set": business_session.model_dump()},
        upsert=True
    )
    
    return business_session.title


# ==================== BUSINESS TOOL ENDPOINTS ====================

@business_router.post("/ads/generate", response_model=APIResponse)
async def generate_ad(request: AdsRequest):
    """
    Generate AI-powered advertisement content
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **product_name**: Name of the product or service
    - **target_audience**: Description of target audience
    - **ad_type**: Type of ad (facebook, google, instagram, linkedin)
    - **key_features**: List of key features to highlight
    - **tone**: Tone of the ad (professional, casual, friendly, etc.)
    """
    try:
        result = await ads_service.generate_ad(
            product_name=request.product_name,
            target_audience=request.target_audience,
            ad_type=request.ad_type,
            key_features=request.key_features,
            tone=request.tone
        )
        
        # Wrap string result in dictionary for storage
        result_dict = {"content": result}
        
        # Save interaction to session
        title = await save_business_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data=result_dict,
            tool_name="Ad Generator"
        )
        
        # Add title to response
        response_with_title = {
            "title": title,
            "content": result
        }
        
        return APIResponse(
            success=True,
            message="Ad generated successfully",
            data=response_with_title
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_router.post("/invoice/generate", response_model=APIResponse)
async def generate_invoice(request: InvoiceRequest):
    """
    Generate professional invoice with automatic calculations
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **company_name**: Your company name
    - **client_name**: Client's name
    - **client_email**: Client's email
    - **items**: List of items [{"name": "Item", "quantity": 1, "price": 100}]
    - **tax_rate**: Tax percentage (optional)
    - **notes**: Additional notes (optional)
    """
    try:
        result = await invoice_service.generate_invoice(
            company_name=request.company_name,
            client_name=request.client_name,
            client_email=request.client_email,
            items=request.items,
            tax_rate=request.tax_rate,
            notes=request.notes
        )
        
        # Wrap string result in dictionary for storage
        result_dict = {"content": result}
        
        # Save interaction to session
        title = await save_business_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data=result_dict,
            tool_name="Invoice Generator"
        )
        
        # Add title to response
        response_with_title = {
            "title": title,
            "content": result
        }
        
        return APIResponse(
            success=True,
            message="Invoice generated successfully",
            data=response_with_title
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_router.post("/email/generate", response_model=APIResponse)
async def generate_email(request: EmailRequest):
    """
    Generate professional emails for various purposes
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **email_type**: Type of email (marketing, followup, cold_outreach, thank_you)
    - **recipient_name**: Recipient's name (optional)
    - **subject**: Email subject line
    - **key_points**: List of key points to include in email
    - **tone**: Email tone (professional, casual, friendly, etc.)
    """
    try:
        result = await email_service.generate_email(
            email_type=request.email_type,
            subject=request.subject,
            key_points=request.key_points,
            recipient_name=request.recipient_name,
            tone=request.tone
        )
        
        # Wrap string result in dictionary for storage
        result_dict = {"content": result}
        
        # Save interaction to session
        title = await save_business_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data=result_dict,
            tool_name="Email Generator"
        )
        
        # Add title to response
        response_with_title = {
            "title": title,
            "content": result
        }
        
        return APIResponse(
            success=True,
            message="Email generated successfully",
            data=response_with_title
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_router.post("/crm/process", response_model=APIResponse)
async def process_crm(request: CRMRequest):
    """
    Process CRM tasks with AI analysis
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **task**: CRM task type (lead_summary, follow_up_schedule, customer_analysis)
    - **customer_data**: Customer information as JSON object
    """
    try:
        result = await crm_service.process_crm_task(
            task=request.task,
            customer_data=request.customer_data
        )
        
        # Wrap string result in dictionary for storage
        result_dict = {"content": result}
        
        # Save interaction to session
        title = await save_business_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data=result_dict,
            tool_name="CRM Tools"
        )
        
        # Add title to response
        response_with_title = {
            "title": title,
            "content": result
        }
        
        return APIResponse(
            success=True,
            message="CRM task processed successfully",
            data=response_with_title
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_router.post("/menu/generate", response_model=APIResponse)
async def generate_menu(request: MenuRequest):
    """
    Generate restaurant menu with items and pricing
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **restaurant_type**: Type of restaurant (cafe, restaurant, bar, fast_food)
    - **cuisine**: Cuisine type (italian, chinese, indian, american, etc.)
    - **items_count**: Number of menu items to generate
    - **price_range**: Price range (low, medium, high)
    """
    try:
        result = await menu_service.generate_menu(
            restaurant_type=request.restaurant_type,
            cuisine=request.cuisine,
            items_count=request.items_count,
            price_range=request.price_range
        )
        
        # Wrap string result in dictionary for storage
        result_dict = {"content": result}
        
        # Save interaction to session
        title = await save_business_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data=result_dict,
            tool_name="Menu Generator"
        )
        
        # Add title to response
        response_with_title = {
            "title": title,
            "content": result
        }
        
        return APIResponse(
            success=True,
            message="Menu generated successfully",
            data=response_with_title
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_router.post("/seo/generate", response_model=APIResponse)
async def generate_seo_content(request: SEORequest):
    """
    Generate SEO-optimized content with meta tags
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **target_keyword**: Primary keyword to optimize for
    - **content_type**: Type of content (blog, product_page, landing_page)
    - **word_count**: Target word count for content
    - **include_meta**: Include meta tags (title, description, keywords)
    """
    try:
        result = await seo_service.generate_seo_content(
            target_keyword=request.target_keyword,
            content_type=request.content_type,
            word_count=request.word_count,
            include_meta=request.include_meta
        )
        
        # Wrap string result in dictionary for storage
        result_dict = {"content": result}
        
        # Save interaction to session
        title = await save_business_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data=result_dict,
            tool_name="SEO Tools"
        )
        
        # Add title to response
        response_with_title = {
            "title": title,
            "content": result
        }
        
        return APIResponse(
            success=True,
            message="SEO content generated successfully",
            data=response_with_title
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_router.post("/product/description", response_model=APIResponse)
async def generate_product_description(request: ProductDescriptionRequest):
    """
    Generate compelling product descriptions
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **product_name**: Name of the product
    - **category**: Product category
    - **features**: List of product features
    - **target_audience**: Target audience description
    - **tone**: Description tone (persuasive, informative, casual, etc.)
    - **length**: Description length (short, medium, long)
    """
    try:
        result = await product_service.generate_product_description(
            product_name=request.product_name,
            category=request.category,
            features=request.features,
            target_audience=request.target_audience,
            tone=request.tone,
            length=request.length
        )
        
        # Wrap string result in dictionary for storage
        result_dict = {"content": result}
        
        # Save interaction to session
        title = await save_business_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data=result_dict,
            tool_name="Product Description"
        )
        
        # Add title to response
        response_with_title = {
            "title": title,
            "content": result
        }
        
        return APIResponse(
            success=True,
            message="Product description generated successfully",
            data=response_with_title
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_router.get("/history/{session_id}", response_model=GenericSessionHistoryResponse, status_code=status.HTTP_200_OK)
async def get_business_session_history(
    session_id: str,
    user_id: str
):
    """
    Get business session history
    
    **Parameters:**
    - session_id: The session ID (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Returns:** All interactions in this business session with the session title
    """
    try:
        collection = database.get_collection_by_name("business_sessions")
        
        # Find session
        session = await collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business session not found or does not belong to user"
            )
        
        business_session = BusinessSession(**session)
        
        return GenericSessionHistoryResponse(
            session_id=business_session.session_id,
            user_id=business_session.user_id,
            title=business_session.title,
            interactions=business_session.interactions,
            created_at=business_session.created_at,
            updated_at=business_session.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve business session history: {str(e)}"
        )


@business_router.delete("/session/{session_id}", status_code=status.HTTP_200_OK)
async def delete_business_session(
    session_id: str,
    user_id: str
):
    """
    Delete a specific business session
    
    **Parameters:**
    - session_id: The session to delete (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Security:** Only the session owner can delete it
    """
    try:
        collection = database.get_collection_by_name("business_sessions")
        
        # Delete session (only if belongs to user)
        result = await collection.delete_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business session not found or does not belong to user"
            )
        
        return {
            "message": "Business session deleted successfully",
            "session_id": session_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete business session: {str(e)}"
        )


@business_router.get("/sessions/list", status_code=status.HTTP_200_OK)
async def list_business_sessions(user_id: str):
    """
    List all business sessions for a user
    
    **Parameters:**
    - user_id: Your user ID (query parameter)
    
    **Returns:** List of all business sessions with title, interaction count, and timestamps
    """
    try:
        collection = database.get_collection_by_name("business_sessions")
        
        # Find all sessions for user
        cursor = collection.find(
            {"user_id": user_id},
            {"session_id": 1, "title": 1, "created_at": 1, "updated_at": 1, "interactions": 1, "_id": 0}
        ).sort("updated_at", -1)
        
        sessions = await cursor.to_list(length=None)
        
        # Add interaction count and title to each session
        session_list = []
        for session in sessions:
            session_list.append({
                "session_id": session["session_id"],
                "title": session.get("title", "New Business Session"),
                "interaction_count": len(session.get("interactions", [])),
                "created_at": session["created_at"],
                "updated_at": session["updated_at"]
            })
        
        return {
            "user_id": user_id,
            "total_sessions": len(session_list),
            "sessions": session_list
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list business sessions: {str(e)}"
        )
