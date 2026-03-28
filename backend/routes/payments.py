"""
AlphaAI Payments & Subscription Routes
Stripe integration for Pro/Elite subscriptions and checkout.
"""
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import os
from database import db, STRIPE_API_KEY, logger
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

router = APIRouter(prefix="/api")

# ============= STRIPE SUBSCRIPTION ENDPOINTS =============

# Pro subscription pricing
PRO_SUBSCRIPTION_PACKAGES = {
    "pro_monthly": {"amount": 29.00, "currency": "usd", "name": "AlphaAI Pro Monthly", "period": "month", "tier": "pro"},
    "pro_yearly": {"amount": 249.00, "currency": "usd", "name": "AlphaAI Pro Yearly", "period": "year", "tier": "pro"},
    "elite_monthly": {"amount": 79.00, "currency": "usd", "name": "AlphaAI Elite Monthly", "period": "month", "tier": "elite"},
    "elite_yearly": {"amount": 699.00, "currency": "usd", "name": "AlphaAI Elite Yearly", "period": "year", "tier": "elite"},
}

class CreateCheckoutRequest(BaseModel):
    package_id: str = "pro_monthly"
    origin_url: str
    wallet_address: Optional[str] = None
    user_email: Optional[str] = None

@router.post("/payments/checkout")
async def create_checkout_session(request: CreateCheckoutRequest, http_request: Request):
    """Create a Stripe checkout session for Pro subscription"""
    try:
        # Validate package
        if request.package_id not in PRO_SUBSCRIPTION_PACKAGES:
            raise HTTPException(status_code=400, detail="Invalid subscription package")
        
        package = PRO_SUBSCRIPTION_PACKAGES[request.package_id]
        
        # Build URLs from frontend origin
        success_url = f"{request.origin_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}&payment=success"
        cancel_url = f"{request.origin_url}/dashboard?payment=cancelled"
        
        # Setup webhook URL
        host_url = str(http_request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        
        # Initialize Stripe checkout
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create metadata
        metadata = {
            "package_id": request.package_id,
            "package_name": package["name"],
            "wallet_address": request.wallet_address or "demo_user",
            "subscription_period": package["period"],
            "target_tier": package.get("tier", "pro"),
            "user_email": request.user_email or ""
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=package["amount"],
            currency=package["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "wallet_address": request.wallet_address or "demo_user",
            "package_id": request.package_id,
            "amount": package["amount"],
            "currency": package["currency"],
            "payment_status": "pending",
            "status": "initiated",
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.payment_transactions.insert_one(transaction)
        
        logger.info(f"Created checkout session: {session.session_id} for package: {request.package_id}")
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "package": package
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, http_request: Request):
    """Get payment status for a checkout session"""
    try:
        # Check if already processed
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        # If already marked as paid, return cached status
        if transaction.get("payment_status") == "paid":
            return {
                "session_id": session_id,
                "status": transaction.get("status"),
                "payment_status": transaction.get("payment_status"),
                "is_pro": True,
                "package_id": transaction.get("package_id"),
                "amount": transaction.get("amount")
            }
        
        # Setup Stripe checkout
        host_url = str(http_request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Get status from Stripe
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction in database
        update_data = {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "updated_at": datetime.now(timezone.utc)
        }
        
        # If payment is successful, mark user as pro
        is_pro = checkout_status.payment_status == "paid"
        if is_pro:
            update_data["pro_activated_at"] = datetime.now(timezone.utc)
            
            # Determine tier from package
            pkg = PRO_SUBSCRIPTION_PACKAGES.get(transaction.get("package_id"), {})
            target_tier = pkg.get("tier", "pro")
            is_elite_pkg = target_tier == "elite"
            
            # Update investor record
            wallet_address = transaction.get("wallet_address")
            if wallet_address and wallet_address != "demo_user":
                await db.investors.update_one(
                    {"wallet_address": wallet_address},
                    {"$set": {"is_pro": True, "is_elite": is_elite_pkg, "pro_since": datetime.now(timezone.utc)}}
                )
            
            # Update user record with user_tier
            user_email = transaction.get("metadata", {}).get("user_email")
            if user_email:
                await db.users.update_one(
                    {"email": user_email},
                    {"$set": {"is_pro": True, "is_elite": is_elite_pkg, "user_tier": target_tier, "pro_since": datetime.now(timezone.utc)}}
                )
        
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        return {
            "session_id": session_id,
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "is_pro": is_pro,
            "amount": checkout_status.amount_total / 100,  # Convert from cents
            "currency": checkout_status.currency,
            "package_id": transaction.get("package_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        host_url = str(request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction based on webhook event
        if webhook_response.session_id:
            update_data = {
                "status": webhook_response.event_type,
                "payment_status": webhook_response.payment_status,
                "webhook_event_id": webhook_response.event_id,
                "updated_at": datetime.now(timezone.utc)
            }
            
            if webhook_response.payment_status == "paid":
                update_data["pro_activated_at"] = datetime.now(timezone.utc)
                
                # Get transaction to find wallet address and tier
                transaction = await db.payment_transactions.find_one({"session_id": webhook_response.session_id})
                if transaction:
                    pkg = PRO_SUBSCRIPTION_PACKAGES.get(transaction.get("package_id"), {})
                    target_tier = pkg.get("tier", "pro")
                    is_elite_pkg = target_tier == "elite"
                    
                    wallet_address = transaction.get("wallet_address")
                    if wallet_address and wallet_address != "demo_user":
                        await db.investors.update_one(
                            {"wallet_address": wallet_address},
                            {"$set": {"is_pro": True, "is_elite": is_elite_pkg, "pro_since": datetime.now(timezone.utc)}}
                        )
                    
                    user_email = transaction.get("metadata", {}).get("user_email")
                    if user_email:
                        await db.users.update_one(
                            {"email": user_email},
                            {"$set": {"is_pro": True, "is_elite": is_elite_pkg, "user_tier": target_tier, "pro_since": datetime.now(timezone.utc)}}
                        )
            
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": update_data}
            )
        
        logger.info(f"Processed webhook: {webhook_response.event_type} for session: {webhook_response.session_id}")
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payments/packages")
async def get_subscription_packages():
    """Get available subscription packages"""
    return {
        "packages": [
            {
                "id": "pro_monthly",
                "name": "AlphaAI Pro Monthly",
                "tier": "pro",
                "price": 29.00,
                "currency": "usd",
                "period": "month",
                "features": [
                    "Real-time AI signals (no delay)",
                    "Live trading enabled",
                    "Copy Trading access",
                    "Full leaderboard access",
                    "Advanced analytics",
                    "Push notifications & email alerts"
                ]
            },
            {
                "id": "pro_yearly",
                "name": "AlphaAI Pro Yearly",
                "tier": "pro",
                "price": 249.00,
                "currency": "usd",
                "period": "year",
                "savings": "Save $99/year",
                "features": [
                    "Everything in Pro Monthly",
                    "2 months FREE"
                ]
            },
            {
                "id": "elite_monthly",
                "name": "AlphaAI Elite Monthly",
                "tier": "elite",
                "price": 79.00,
                "currency": "usd",
                "period": "month",
                "features": [
                    "Everything in Pro",
                    "Priority signal delivery",
                    "Early access to new features",
                    "Higher rate limits",
                    "Advanced research tools"
                ]
            },
            {
                "id": "elite_yearly",
                "name": "AlphaAI Elite Yearly",
                "tier": "elite",
                "price": 699.00,
                "currency": "usd",
                "period": "year",
                "savings": "Save $249/year",
                "features": [
                    "Everything in Elite Monthly",
                    "2 months FREE"
                ]
            }
        ]
    }

@router.get("/users/pro-status/{wallet_address}")
async def get_pro_status(wallet_address: str):
    """Check if a user has Pro/Elite subscription"""
    investor = await db.investors.find_one({"wallet_address": wallet_address})
    if not investor:
        return {"is_pro": False, "is_elite": False, "user_tier": "free", "wallet_address": wallet_address}
    
    user_tier = "free"
    if investor.get("is_elite"):
        user_tier = "elite"
    elif investor.get("is_pro"):
        user_tier = "pro"
    
    return {
        "is_pro": investor.get("is_pro", False),
        "is_elite": investor.get("is_elite", False),
        "user_tier": user_tier,
        "pro_since": investor.get("pro_since"),
        "wallet_address": wallet_address
    }

@router.get("/documentation/download")
async def download_documentation():
    """Download the complete platform documentation PDF"""
    pdf_path = ROOT_DIR / "reports" / "AlphaAI_Complete_Documentation.pdf"
    
    if not pdf_path.exists():
        # Generate if not exists
        import subprocess
        subprocess.run(["python", str(ROOT_DIR / "generate_platform_documentation.py")], cwd=str(ROOT_DIR))
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Documentation PDF not found")
    
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename="AlphaAI_Complete_Documentation.pdf",
        headers={
            "Content-Disposition": "attachment; filename=AlphaAI_Complete_Documentation.pdf",
            "Cache-Control": "no-cache"
        }
    )

@router.get("/documentation/regenerate")
async def regenerate_documentation():
    """Regenerate the platform documentation PDF"""
    import subprocess
    result = subprocess.run(
        ["python", str(ROOT_DIR / "generate_platform_documentation.py")], 
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {result.stderr}")
    
    return {"message": "Documentation regenerated successfully", "path": "/api/documentation/download"}

@router.get("/documentation/business")
async def download_business_pdf():
    """Download the business-focused PDF for investors"""
    pdf_path = ROOT_DIR / "reports" / "AlphaAI_Business_Overview.pdf"
    
    if not pdf_path.exists():
        import subprocess
        subprocess.run(["python", str(ROOT_DIR / "generate_business_documentation.py")], cwd=str(ROOT_DIR))
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Business PDF not found")
    
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename="AlphaAI_Business_Overview.pdf",
        headers={
            "Content-Disposition": "attachment; filename=AlphaAI_Business_Overview.pdf",
            "Cache-Control": "no-cache"
        }
    )

# ============= A/B TESTING & CONVERSION ANALYTICS =============
