"""
AlphaAI Authentication Routes
- Email/Password Registration & Login
- JWT Token Management
- Email Verification
- Password Reset
- Optional 2FA (TOTP)
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import secrets
import logging
import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from passlib.context import CryptContext
from jose import JWTError, jwt

# Import email service
from services.email_service import (
    send_verification_email,
    send_password_reset_email,
    send_2fa_enabled_email
)

# Setup
logger = logging.getLogger("AlphaAI.Auth")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# App URL for email links
APP_URL = os.environ.get("APP_URL", "https://alphaai.com")

# MongoDB connection - will be initialized in main server
db = None

def init_db(database):
    """Initialize database connection"""
    global db
    db = database

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ============= MODELS =============

class UserBase(BaseModel):
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)

class UserLogin(UserBase):
    password: str
    totp_code: Optional[str] = None  # For 2FA

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    is_verified: bool
    is_pro: bool
    is_elite: bool
    has_2fa: bool
    wallet_address: Optional[str] = None
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class Enable2FAResponse(BaseModel):
    secret: str
    qr_code: str  # Base64 encoded QR code
    backup_codes: list[str]

class Verify2FARequest(BaseModel):
    totp_code: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LinkWalletRequest(BaseModel):
    wallet_address: str

class VerifyEmailRequest(BaseModel):
    token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

# ============= HELPER FUNCTIONS =============

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)

def generate_backup_codes(count: int = 8) -> list[str]:
    """Generate backup codes for 2FA recovery"""
    return [secrets.token_hex(4).upper() for _ in range(count)]

async def get_user_by_email(email: str) -> Optional[dict]:
    """Fetch user by email from database"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    user = await db.users.find_one({"email": email.lower()}, {"_id": 0})
    return user

async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Fetch user by ID from database"""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    return user

async def get_current_user(request: Request) -> dict:
    """Dependency to get current authenticated user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = await get_user_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def format_user_response(user: dict) -> UserResponse:
    """Format user dict into UserResponse"""
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        is_verified=user.get("is_verified", False),
        is_pro=user.get("is_pro", False),
        is_elite=user.get("is_elite", False),
        has_2fa=user.get("has_2fa", False),
        wallet_address=user.get("wallet_address"),
        created_at=user.get("created_at", datetime.now(timezone.utc))
    )

# ============= ROUTES =============

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, background_tasks: BackgroundTasks):
    """Register a new user with email and password"""
    # Check if email already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    verification_token = generate_verification_token()
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    new_user = {
        "id": user_id,
        "email": user_data.email.lower(),
        "name": user_data.name,
        "password_hash": hash_password(user_data.password),
        "is_verified": False,
        "is_pro": False,
        "is_elite": False,
        "has_2fa": False,
        "totp_secret": None,
        "backup_codes": [],
        "wallet_address": None,
        "verification_token": verification_token,
        "verification_token_expires": now + timedelta(hours=24),
        "paper_balance": 10000.0,
        "paper_pnl": 0.0,
        "created_at": now,
        "updated_at": now
    }
    
    await db.users.insert_one(new_user)
    
    # Send verification email (background task)
    background_tasks.add_task(
        send_verification_email,
        user_data.email,
        user_data.name,
        verification_token,
        APP_URL
    )
    logger.info(f"User registered: {user_data.email} (verification email queued)")
    
    # Generate tokens
    access_token = create_access_token({"sub": user_id, "email": user_data.email.lower()})
    refresh_token = create_refresh_token({"sub": user_id})
    
    # Store refresh token
    await db.refresh_tokens.insert_one({
        "user_id": user_id,
        "token": refresh_token,
        "created_at": now,
        "expires_at": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=format_user_response(new_user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password (+ optional 2FA code)"""
    user = await get_user_by_email(credentials.email)
    
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check 2FA if enabled
    if user.get("has_2fa"):
        if not credentials.totp_code:
            raise HTTPException(
                status_code=403, 
                detail={"message": "2FA code required", "requires_2fa": True}
            )
        
        totp = pyotp.TOTP(user["totp_secret"])
        # Check TOTP code or backup codes
        if not totp.verify(credentials.totp_code, valid_window=1):
            # Check backup codes
            backup_codes = user.get("backup_codes", [])
            if credentials.totp_code.upper() in backup_codes:
                # Remove used backup code
                backup_codes.remove(credentials.totp_code.upper())
                await db.users.update_one(
                    {"id": user["id"]},
                    {"$set": {"backup_codes": backup_codes}}
                )
            else:
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Generate tokens
    now = datetime.now(timezone.utc)
    access_token = create_access_token({"sub": user["id"], "email": user["email"]})
    refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Store refresh token
    await db.refresh_tokens.insert_one({
        "user_id": user["id"],
        "token": refresh_token,
        "created_at": now,
        "expires_at": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    })
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": now, "updated_at": now}}
    )
    
    logger.info(f"User logged in: {user['email']}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=format_user_response(user)
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(request: RefreshTokenRequest):
    """Get new access token using refresh token"""
    payload = decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Verify refresh token exists in DB
    stored_token = await db.refresh_tokens.find_one({"token": request.refresh_token})
    if not stored_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or expired")
    
    user = await get_user_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Generate new tokens
    now = datetime.now(timezone.utc)
    new_access_token = create_access_token({"sub": user["id"], "email": user["email"]})
    new_refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Revoke old refresh token and store new one
    await db.refresh_tokens.delete_one({"token": request.refresh_token})
    await db.refresh_tokens.insert_one({
        "user_id": user["id"],
        "token": new_refresh_token,
        "created_at": now,
        "expires_at": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    })
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=format_user_response(user)
    )

@router.post("/logout")
async def logout(request: Request, user: dict = Depends(get_current_user)):
    """Logout and revoke refresh tokens"""
    await db.refresh_tokens.delete_many({"user_id": user["id"]})
    logger.info(f"User logged out: {user['email']}")
    return {"message": "Logged out successfully"}

@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest):
    """Verify email address using token"""
    user = await db.users.find_one(
        {"verification_token": data.token},
        {"_id": 0}
    )
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    if user.get("is_verified"):
        return {"message": "Email already verified"}
    
    if datetime.now(timezone.utc) > user.get("verification_token_expires", datetime.now(timezone.utc)):
        raise HTTPException(status_code=400, detail="Verification token expired")
    
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "is_verified": True,
                "verification_token": None,
                "verification_token_expires": None,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    logger.info(f"Email verified: {user['email']}")
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(user: dict = Depends(get_current_user), background_tasks: BackgroundTasks = None):
    """Resend verification email"""
    if user.get("is_verified"):
        return {"message": "Email already verified"}
    
    verification_token = generate_verification_token()
    now = datetime.now(timezone.utc)
    
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "verification_token": verification_token,
                "verification_token_expires": now + timedelta(hours=24),
                "updated_at": now
            }
        }
    )
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        user["email"],
        user["name"],
        verification_token,
        APP_URL
    )
    logger.info(f"Verification email resent: {user['email']}")
    
    return {"message": "Verification email sent"}

@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, background_tasks: BackgroundTasks):
    """Request password reset email"""
    user = await get_user_by_email(data.email)
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If an account exists with this email, a reset link has been sent"}
    
    reset_token = generate_verification_token()
    now = datetime.now(timezone.utc)
    
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "reset_token": reset_token,
                "reset_token_expires": now + timedelta(hours=1),
                "updated_at": now
            }
        }
    )
    
    # Send password reset email
    background_tasks.add_task(
        send_password_reset_email,
        user["email"],
        user["name"],
        reset_token,
        APP_URL
    )
    logger.info(f"Password reset email sent: {user['email']}")
    
    return {"message": "If an account exists with this email, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm):
    """Reset password using token"""
    user = await db.users.find_one(
        {"reset_token": data.token},
        {"_id": 0}
    )
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if datetime.now(timezone.utc) > user.get("reset_token_expires", datetime.now(timezone.utc)):
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_hash": hash_password(data.new_password),
                "reset_token": None,
                "reset_token_expires": None,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Revoke all refresh tokens for security
    await db.refresh_tokens.delete_many({"user_id": user["id"]})
    
    logger.info(f"Password reset completed: {user['email']}")
    return {"message": "Password reset successfully"}

@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    """Change password for authenticated user"""
    # Fetch full user with password hash
    full_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    
    if not verify_password(data.current_password, full_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_hash": hash_password(data.new_password),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    logger.info(f"Password changed: {user['email']}")
    return {"message": "Password changed successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return format_user_response(user)

@router.post("/link-wallet")
async def link_wallet(data: LinkWalletRequest, user: dict = Depends(get_current_user)):
    """Link a Web3 wallet address to the account"""
    # Check if wallet is already linked to another account
    existing = await db.users.find_one(
        {"wallet_address": data.wallet_address.lower(), "id": {"$ne": user["id"]}},
        {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Wallet already linked to another account")
    
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "wallet_address": data.wallet_address.lower(),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    logger.info(f"Wallet linked: {user['email']} -> {data.wallet_address}")
    return {"message": "Wallet linked successfully", "wallet_address": data.wallet_address}

# ============= 2FA ROUTES =============

@router.post("/2fa/enable", response_model=Enable2FAResponse)
async def enable_2fa(user: dict = Depends(get_current_user)):
    """Enable 2FA - returns secret and QR code"""
    if user.get("has_2fa"):
        raise HTTPException(status_code=400, detail="2FA is already enabled")
    
    # Generate TOTP secret
    secret = pyotp.random_base32()
    backup_codes = generate_backup_codes()
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user["email"],
        issuer_name="AlphaAI"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Store secret temporarily (not activated until verified)
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "pending_totp_secret": secret,
                "pending_backup_codes": backup_codes,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return Enable2FAResponse(
        secret=secret,
        qr_code=f"data:image/png;base64,{qr_code_base64}",
        backup_codes=backup_codes
    )

@router.post("/2fa/verify")
async def verify_2fa_setup(data: Verify2FARequest, user: dict = Depends(get_current_user), background_tasks: BackgroundTasks = None):
    """Verify 2FA setup with TOTP code"""
    # Get pending secret
    full_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    pending_secret = full_user.get("pending_totp_secret")
    
    if not pending_secret:
        raise HTTPException(status_code=400, detail="No pending 2FA setup found")
    
    # Verify TOTP code
    totp = pyotp.TOTP(pending_secret)
    if not totp.verify(data.totp_code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid verification code")
    
    # Activate 2FA
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "has_2fa": True,
                "totp_secret": pending_secret,
                "backup_codes": full_user.get("pending_backup_codes", []),
                "pending_totp_secret": None,
                "pending_backup_codes": None,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Send 2FA enabled confirmation email
    if background_tasks:
        background_tasks.add_task(
            send_2fa_enabled_email,
            user["email"],
            user["name"]
        )
    
    logger.info(f"2FA enabled: {user['email']}")
    return {"message": "2FA enabled successfully"}

@router.post("/2fa/disable")
async def disable_2fa(data: Verify2FARequest, user: dict = Depends(get_current_user)):
    """Disable 2FA with TOTP code verification"""
    full_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    
    if not full_user.get("has_2fa"):
        raise HTTPException(status_code=400, detail="2FA is not enabled")
    
    # Verify TOTP code
    totp = pyotp.TOTP(full_user["totp_secret"])
    if not totp.verify(data.totp_code, valid_window=1):
        # Check backup codes
        backup_codes = full_user.get("backup_codes", [])
        if data.totp_code.upper() not in backup_codes:
            raise HTTPException(status_code=401, detail="Invalid verification code")
    
    # Disable 2FA
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "has_2fa": False,
                "totp_secret": None,
                "backup_codes": [],
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    logger.info(f"2FA disabled: {user['email']}")
    return {"message": "2FA disabled successfully"}

@router.get("/2fa/backup-codes")
async def get_backup_codes(user: dict = Depends(get_current_user)):
    """Get remaining backup codes count"""
    full_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    backup_codes = full_user.get("backup_codes", [])
    return {"remaining_codes": len(backup_codes)}

@router.post("/2fa/regenerate-backup-codes")
async def regenerate_backup_codes(data: Verify2FARequest, user: dict = Depends(get_current_user)):
    """Regenerate backup codes with TOTP verification"""
    full_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    
    if not full_user.get("has_2fa"):
        raise HTTPException(status_code=400, detail="2FA is not enabled")
    
    # Verify TOTP code
    totp = pyotp.TOTP(full_user["totp_secret"])
    if not totp.verify(data.totp_code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid verification code")
    
    new_backup_codes = generate_backup_codes()
    
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "backup_codes": new_backup_codes,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    logger.info(f"Backup codes regenerated: {user['email']}")
    return {"backup_codes": new_backup_codes}
