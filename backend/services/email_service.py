"""
AlphaAI Email Service
Handles transactional emails for authentication flows:
- Email verification
- Password reset
- Welcome emails
- Pro subscription confirmation
"""
import os
import asyncio
import logging
import resend
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("AlphaAI.Email")

# Initialize Resend
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
APP_NAME = "AlphaAI"
APP_URL = os.environ.get("APP_URL", "https://alphaai.com")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend API initialized")
else:
    logger.warning("RESEND_API_KEY not set - emails will be logged only")

# Email Templates
def get_verification_email_html(name: str, verification_url: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #050505; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #050505; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #121212; border-radius: 16px; border: 1px solid #27272a;">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #7B61FF, #00FF94); border-radius: 12px; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-size: 28px; color: white;">⚡</span>
                                </div>
                                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">Welcome to {APP_NAME}</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 20px 40px;">
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Hi {name},
                                </p>
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Thanks for signing up! Please verify your email address to get started with AI-powered crypto trading signals.
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="padding: 20px 0;">
                                            <a href="{verification_url}" style="display: inline-block; background: linear-gradient(135deg, #7B61FF, #6B51EF); color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 50px; font-size: 16px; font-weight: 600;">
                                                Verify Email Address
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #71717a; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                                    Or copy this link to your browser:<br>
                                    <a href="{verification_url}" style="color: #7B61FF; word-break: break-all;">{verification_url}</a>
                                </p>
                                
                                <p style="color: #71717a; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                                    This link expires in 24 hours.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 30px 40px; border-top: 1px solid #27272a;">
                                <p style="color: #52525b; font-size: 12px; line-height: 1.5; margin: 0; text-align: center;">
                                    If you didn't create an account with {APP_NAME}, you can safely ignore this email.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_password_reset_email_html(name: str, reset_url: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #050505; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #050505; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #121212; border-radius: 16px; border: 1px solid #27272a;">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #FFB800, #FF8C00); border-radius: 12px; margin: 0 auto 20px auto;">
                                    <span style="font-size: 28px; line-height: 60px;">🔐</span>
                                </div>
                                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">Reset Your Password</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 20px 40px;">
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Hi {name},
                                </p>
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    We received a request to reset your password. Click the button below to create a new password.
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="padding: 20px 0;">
                                            <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #FFB800, #FF8C00); color: #000000; text-decoration: none; padding: 14px 32px; border-radius: 50px; font-size: 16px; font-weight: 600;">
                                                Reset Password
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #71717a; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                                    Or copy this link to your browser:<br>
                                    <a href="{reset_url}" style="color: #FFB800; word-break: break-all;">{reset_url}</a>
                                </p>
                                
                                <p style="color: #71717a; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                                    This link expires in 1 hour. If you didn't request this, please ignore this email.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Security Notice -->
                        <tr>
                            <td style="padding: 0 40px 30px 40px;">
                                <div style="background-color: #1a1a1a; border-radius: 8px; padding: 16px; border-left: 3px solid #FFB800;">
                                    <p style="color: #a1a1aa; font-size: 13px; margin: 0;">
                                        <strong style="color: #FFB800;">Security tip:</strong> {APP_NAME} will never ask for your password via email.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 40px; border-top: 1px solid #27272a;">
                                <p style="color: #52525b; font-size: 12px; line-height: 1.5; margin: 0; text-align: center;">
                                    If you didn't request a password reset, you can safely ignore this email.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_welcome_pro_email_html(name: str, plan: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #050505; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #050505; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #121212; border-radius: 16px; border: 1px solid #7B61FF;">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, rgba(123, 97, 255, 0.1), rgba(0, 255, 148, 0.1)); border-radius: 16px 16px 0 0;">
                                <div style="font-size: 48px; margin-bottom: 16px;">🎉</div>
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">Welcome to {APP_NAME} Pro!</h1>
                                <p style="color: #7B61FF; font-size: 14px; margin: 8px 0 0 0; font-weight: 500;">{plan}</p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px 40px;">
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Hi {name},
                                </p>
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Thank you for upgrading to Pro! You now have access to all premium features:
                                </p>
                                
                                <!-- Features List -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td style="padding: 12px 0;">
                                            <table cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="width: 24px; color: #00FF94; font-size: 16px;">✓</td>
                                                    <td style="color: #e4e4e7; font-size: 15px;">Real-time AI trading signals (no 15-min delay)</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 0;">
                                            <table cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="width: 24px; color: #00FF94; font-size: 16px;">✓</td>
                                                    <td style="color: #e4e4e7; font-size: 15px;">WebSocket live price updates</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 0;">
                                            <table cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="width: 24px; color: #00FF94; font-size: 16px;">✓</td>
                                                    <td style="color: #e4e4e7; font-size: 15px;">Advanced performance analytics</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px 0;">
                                            <table cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="width: 24px; color: #00FF94; font-size: 16px;">✓</td>
                                                    <td style="color: #e4e4e7; font-size: 15px;">Priority support</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="padding: 30px 0 20px 0;">
                                            <a href="{APP_URL}/dashboard" style="display: inline-block; background: linear-gradient(135deg, #7B61FF, #00FF94); color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 50px; font-size: 16px; font-weight: 600;">
                                                Go to Dashboard
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 40px; border-top: 1px solid #27272a;">
                                <p style="color: #52525b; font-size: 12px; line-height: 1.5; margin: 0; text-align: center;">
                                    Questions? Reply to this email or contact support@alphaai.com
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_2fa_enabled_email_html(name: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #050505; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #050505; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #121212; border-radius: 16px; border: 1px solid #27272a;">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #00FF94, #00CC76); border-radius: 12px; margin: 0 auto 20px auto;">
                                    <span style="font-size: 28px; line-height: 60px;">🛡️</span>
                                </div>
                                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">2FA Enabled Successfully</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 20px 40px 30px 40px;">
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Hi {name},
                                </p>
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Two-factor authentication has been successfully enabled on your {APP_NAME} account. Your account is now more secure!
                                </p>
                                
                                <div style="background-color: #1a1a1a; border-radius: 8px; padding: 16px; border-left: 3px solid #00FF94; margin-top: 20px;">
                                    <p style="color: #a1a1aa; font-size: 13px; margin: 0;">
                                        <strong style="color: #00FF94;">Important:</strong> Keep your backup codes in a safe place. You'll need them if you lose access to your authenticator app.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 40px; border-top: 1px solid #27272a;">
                                <p style="color: #52525b; font-size: 12px; line-height: 1.5; margin: 0; text-align: center;">
                                    If you didn't enable 2FA, please contact support immediately.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# Email sending functions
async def send_email(to_email: str, subject: str, html_content: str) -> dict:
    """Send an email using Resend API"""
    if not RESEND_API_KEY:
        # Log-only mode when no API key
        logger.info(f"[EMAIL LOG] To: {to_email}, Subject: {subject}")
        return {"status": "logged", "message": "Email logged (no API key configured)"}
    
    params = {
        "from": SENDER_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {subject}")
        return {"status": "sent", "email_id": email.get("id")}
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return {"status": "error", "error": str(e)}


async def send_verification_email(to_email: str, name: str, verification_token: str, base_url: str) -> dict:
    """Send email verification link"""
    verification_url = f"{base_url}/verify-email?token={verification_token}"
    html_content = get_verification_email_html(name, verification_url)
    return await send_email(to_email, f"Verify your {APP_NAME} email", html_content)


async def send_password_reset_email(to_email: str, name: str, reset_token: str, base_url: str) -> dict:
    """Send password reset link"""
    reset_url = f"{base_url}/reset-password?token={reset_token}"
    html_content = get_password_reset_email_html(name, reset_url)
    return await send_email(to_email, f"Reset your {APP_NAME} password", html_content)


async def send_welcome_pro_email(to_email: str, name: str, plan: str) -> dict:
    """Send welcome email after Pro upgrade"""
    html_content = get_welcome_pro_email_html(name, plan)
    return await send_email(to_email, f"Welcome to {APP_NAME} Pro! 🎉", html_content)


async def send_2fa_enabled_email(to_email: str, name: str) -> dict:
    """Send confirmation when 2FA is enabled"""
    html_content = get_2fa_enabled_email_html(name)
    return await send_email(to_email, f"2FA Enabled on your {APP_NAME} account", html_content)
