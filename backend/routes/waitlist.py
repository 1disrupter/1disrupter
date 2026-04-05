"""
Waitlist Automation — 3-email drip sequence via Resend.
Endpoints: POST /api/waitlist, GET /api/waitlist/admin/analytics
Background scheduler processes delayed emails (Email #2 at +24h, Email #3 at +72h).
"""
import os
import uuid
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, EmailStr

from database import db
from services.email_service import send_email, APP_URL, APP_NAME

logger = logging.getLogger("AlphaAI.Waitlist")
router = APIRouter(prefix="/api/waitlist", tags=["Waitlist"])

waitlist_col = db["waitlist"]
email_jobs_col = db["waitlist_email_jobs"]

# ═══════════════════════════════════════════
#  EMAIL TEMPLATES
# ═══════════════════════════════════════════

def _base_template(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#050505;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#050505;padding:40px 20px;"><tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#121212;border-radius:16px;border:1px solid #27272a;">
<tr><td style="padding:40px 40px 20px;text-align:center;">
  <h1 style="color:#fff;margin:0;font-size:24px;font-weight:600;">{title}</h1>
  <p style="color:#a1a1aa;font-size:11px;letter-spacing:0.15em;text-transform:uppercase;margin:6px 0 0;font-weight:300;">{APP_NAME} Signal Intelligence</p>
</td></tr>
<tr><td style="padding:20px 40px 30px;">{body_html}</td></tr>
<tr><td style="padding:20px 40px;border-top:1px solid #27272a;">
  <p style="color:#52525b;font-size:11px;margin:0;text-align:center;">
    You're receiving this because you joined the {APP_NAME} waitlist.
    <br><a href="{APP_URL}/api/waitlist/unsubscribe?email={{email}}" style="color:#52525b;text-decoration:underline;">Unsubscribe</a>
  </p>
</td></tr>
</table></td></tr></table></body></html>"""


def email_welcome(email: str) -> tuple:
    subject = "Welcome to AlphaAI — You're In"
    body = f"""
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:0 0 20px;">
      Thanks for joining the {APP_NAME} waitlist! You're now part of an exclusive group
      getting early access to AI-powered crypto trading signals.
    </p>
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:0 0 20px;">
      {APP_NAME} uses machine-learning models to detect momentum shifts, mean-reversion setups,
      and breakout patterns — delivering signals with confidence scores before the crowd moves.
    </p>
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:0 0 30px;">
      Explore the platform right now in <strong style="color:#00FF94;">Demo Mode</strong> — no signup or credit card required.
    </p>
    <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:10px 0;">
      <a href="{APP_URL}" style="display:inline-block;background:linear-gradient(135deg,#7B61FF,#6B51EF);color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:16px;font-weight:600;">
        Explore AlphaAI
      </a>
    </td></tr></table>
    """
    html = _base_template("Welcome to AlphaAI", body).replace("{email}", email)
    return subject, html


def email_activation(email: str) -> tuple:
    subject = "Your AlphaAI Dashboard Is Ready"
    body = f"""
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:0 0 20px;">
      Your dashboard is live and ready to explore. Here's how to get value in 60 seconds:
    </p>
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="padding:8px 0;"><table cellpadding="0" cellspacing="0"><tr>
        <td style="width:24px;color:#00FF94;font-size:16px;">1.</td>
        <td style="color:#e4e4e7;font-size:15px;">Visit the <a href="{APP_URL}/strategies" style="color:#7B61FF;text-decoration:underline;">Strategy Leaderboard</a></td>
      </tr></table></td></tr>
      <tr><td style="padding:8px 0;"><table cellpadding="0" cellspacing="0"><tr>
        <td style="width:24px;color:#00FF94;font-size:16px;">2.</td>
        <td style="color:#e4e4e7;font-size:15px;">Browse our <strong>Featured Strategies</strong> — each with verified Sharpe ratios and win rates</td>
      </tr></table></td></tr>
      <tr><td style="padding:8px 0;"><table cellpadding="0" cellspacing="0"><tr>
        <td style="width:24px;color:#00FF94;font-size:16px;">3.</td>
        <td style="color:#e4e4e7;font-size:15px;">Click <strong>"View Strategy"</strong> to see full performance and logic</td>
      </tr></table></td></tr>
    </table>
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:20px 0 30px;">
      Top strategies right now: <strong style="color:#fff;">Alpha Momentum BTC</strong> (+47.2% return),
      <strong style="color:#fff;">SOL Breakout Pulse</strong> (+63.7% return).
    </p>
    <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:10px 0;">
      <a href="{APP_URL}/strategies" style="display:inline-block;background:linear-gradient(135deg,#7B61FF,#00FF94);color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:16px;font-weight:600;">
        View Strategy Leaderboard
      </a>
    </td></tr></table>
    """
    html = _base_template("Your Dashboard Is Ready", body).replace("{email}", email)
    return subject, html


def email_conversion(email: str) -> tuple:
    subject = "Your First Strategy Is Waiting"
    body = f"""
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:0 0 20px;">
      You've been exploring {APP_NAME} — now it's time to unlock the full experience.
    </p>
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:0 0 20px;">
      With a Pro subscription, you get:
    </p>
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="padding:8px 0;"><table cellpadding="0" cellspacing="0"><tr>
        <td style="width:24px;color:#00FF94;font-size:16px;">&#10003;</td>
        <td style="color:#e4e4e7;font-size:15px;"><strong>Real-time AI signals</strong> — no 15-minute delay</td>
      </tr></table></td></tr>
      <tr><td style="padding:8px 0;"><table cellpadding="0" cellspacing="0"><tr>
        <td style="width:24px;color:#00FF94;font-size:16px;">&#10003;</td>
        <td style="color:#e4e4e7;font-size:15px;"><strong>Live events feed</strong> — signals, trades, and updates via WebSocket</td>
      </tr></table></td></tr>
      <tr><td style="padding:8px 0;"><table cellpadding="0" cellspacing="0"><tr>
        <td style="width:24px;color:#00FF94;font-size:16px;">&#10003;</td>
        <td style="color:#e4e4e7;font-size:15px;"><strong>Copy top strategies</strong> to your own lab and customize</td>
      </tr></table></td></tr>
      <tr><td style="padding:8px 0;"><table cellpadding="0" cellspacing="0"><tr>
        <td style="width:24px;color:#00FF94;font-size:16px;">&#10003;</td>
        <td style="color:#e4e4e7;font-size:15px;"><strong>Priority support</strong> and advanced performance analytics</td>
      </tr></table></td></tr>
    </table>
    <p style="color:#a1a1aa;font-size:16px;line-height:1.6;margin:20px 0 30px;">
      Your first strategy is waiting. Start making data-driven trades today.
    </p>
    <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:10px 0;">
      <a href="{APP_URL}/pricing" style="display:inline-block;background:linear-gradient(135deg,#FFB800,#FF8C00);color:#000;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:16px;font-weight:600;">
        Upgrade to Pro
      </a>
    </td></tr></table>
    """
    html = _base_template("Your First Strategy Is Waiting", body).replace("{email}", email)
    return subject, html


EMAIL_SEQUENCE = [
    {"step": 1, "name": "welcome", "delay_hours": 0, "fn": email_welcome, "next_status": "pending"},
    {"step": 2, "name": "activation", "delay_hours": 24, "fn": email_activation, "next_status": "activated"},
    {"step": 3, "name": "conversion", "delay_hours": 72, "fn": email_conversion, "next_status": "converted"},
]


# ═══════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════

async def _schedule_email(email: str, waitlist_id: str, step: dict, base_time: datetime):
    """Create a scheduled email job in the database."""
    scheduled_for = base_time + timedelta(hours=step["delay_hours"])
    job = {
        "id": str(uuid.uuid4()),
        "waitlist_id": waitlist_id,
        "email": email,
        "step": step["step"],
        "step_name": step["name"],
        "scheduled_for": scheduled_for.isoformat(),
        "status": "pending",
        "sent_at": None,
        "error": None,
        "created_at": base_time.isoformat(),
    }
    await email_jobs_col.insert_one(job)
    return job


async def _send_and_log(email: str, waitlist_id: str, step: dict):
    """Send an email and log the result."""
    subject, html = step["fn"](email)
    result = await send_email(email, subject, html)

    now = datetime.now(timezone.utc)
    log_entry = {
        "step": step["step"],
        "step_name": step["name"],
        "subject": subject,
        "status": result.get("status", "error"),
        "error": result.get("error"),
        "sent_at": now.isoformat(),
    }

    # Append to waitlist entry delivery_logs
    await waitlist_col.update_one(
        {"id": waitlist_id},
        {
            "$push": {"delivery_logs": log_entry},
            "$set": {"status": step["next_status"], "updated_at": now.isoformat()},
        },
    )

    # Update job status
    await email_jobs_col.update_one(
        {"waitlist_id": waitlist_id, "step": step["step"]},
        {"$set": {"status": result.get("status", "error"), "sent_at": now.isoformat(), "error": result.get("error")}},
    )

    logger.info(f"Waitlist email #{step['step']} ({step['name']}) → {email}: {result.get('status')}")
    return result


# ═══════════════════════════════════════════
#  BACKGROUND SCHEDULER
# ═══════════════════════════════════════════

_scheduler_running = False

async def start_email_scheduler():
    """Background loop that checks for pending email jobs and sends them."""
    global _scheduler_running
    if _scheduler_running:
        return
    _scheduler_running = True
    logger.info("Waitlist email scheduler started")

    while True:
        try:
            now = datetime.now(timezone.utc)
            pending_jobs = await email_jobs_col.find({
                "status": "pending",
                "scheduled_for": {"$lte": now.isoformat()},
            }, {"_id": 0}).to_list(20)

            for job in pending_jobs:
                step_info = next((s for s in EMAIL_SEQUENCE if s["step"] == job["step"]), None)
                if step_info:
                    await _send_and_log(job["email"], job["waitlist_id"], step_info)

        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        await asyncio.sleep(30)  # Check every 30 seconds


# ═══════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════

class WaitlistRequest(BaseModel):
    email: EmailStr


@router.post("")
async def join_waitlist(req: WaitlistRequest, bg: BackgroundTasks):
    """Add email to waitlist and trigger 3-email sequence."""
    email = req.email.lower().strip()

    # Idempotent — don't re-add existing entries
    existing = await waitlist_col.find_one({"email": email}, {"_id": 0})
    if existing:
        return {"message": "Already on the waitlist", "waitlist_id": existing["id"], "duplicate": True}

    now = datetime.now(timezone.utc)
    waitlist_id = str(uuid.uuid4())

    entry = {
        "id": waitlist_id,
        "email": email,
        "status": "pending",
        "delivery_logs": [],
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    await waitlist_col.insert_one(entry)

    # Schedule all 3 emails
    for step in EMAIL_SEQUENCE:
        await _schedule_email(email, waitlist_id, step, now)

    # Send Email #1 immediately in background
    bg.add_task(_send_and_log, email, waitlist_id, EMAIL_SEQUENCE[0])

    # Start scheduler if not running
    bg.add_task(start_email_scheduler)

    logger.info(f"Waitlist signup: {email} (id={waitlist_id})")
    return {"message": "Welcome to the waitlist!", "waitlist_id": waitlist_id, "duplicate": False}


@router.get("/unsubscribe")
async def unsubscribe(email: str = Query(...)):
    """Unsubscribe from waitlist emails."""
    result = await waitlist_col.update_one(
        {"email": email.lower().strip()},
        {"$set": {"status": "unsubscribed", "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    # Cancel pending jobs
    await email_jobs_col.update_many(
        {"email": email.lower().strip(), "status": "pending"},
        {"$set": {"status": "cancelled"}},
    )
    return {"message": "You have been unsubscribed from waitlist emails."}


# ═══════════════════════════════════════════
#  ADMIN ANALYTICS
# ═══════════════════════════════════════════

@router.get("/admin/analytics")
async def waitlist_analytics(admin_key: str = Query(...)):
    """Admin: Waitlist funnel analytics."""
    if admin_key != os.environ.get("ADMIN_SECRET", "alphaai_admin_2026"):
        raise HTTPException(status_code=403, detail="Admin access denied")

    total = await waitlist_col.count_documents({})
    pending = await waitlist_col.count_documents({"status": "pending"})
    activated = await waitlist_col.count_documents({"status": "activated"})
    converted = await waitlist_col.count_documents({"status": "converted"})
    unsubscribed = await waitlist_col.count_documents({"status": "unsubscribed"})

    # Email delivery stats
    total_jobs = await email_jobs_col.count_documents({})
    sent_jobs = await email_jobs_col.count_documents({"status": "sent"})
    failed_jobs = await email_jobs_col.count_documents({"status": "error"})
    pending_jobs = await email_jobs_col.count_documents({"status": "pending"})

    # Per-step breakdown
    step_stats = []
    for step in EMAIL_SEQUENCE:
        s_total = await email_jobs_col.count_documents({"step": step["step"]})
        s_sent = await email_jobs_col.count_documents({"step": step["step"], "status": "sent"})
        s_failed = await email_jobs_col.count_documents({"step": step["step"], "status": "error"})
        step_stats.append({
            "step": step["step"],
            "name": step["name"],
            "total": s_total,
            "sent": s_sent,
            "failed": s_failed,
            "delivery_rate": round(s_sent / s_total * 100, 1) if s_total > 0 else 0,
        })

    return {
        "total_waitlist": total,
        "funnel": {
            "pending": pending,
            "activated": activated,
            "converted": converted,
            "unsubscribed": unsubscribed,
        },
        "activation_rate": round(activated / total * 100, 1) if total > 0 else 0,
        "conversion_rate": round(converted / total * 100, 1) if total > 0 else 0,
        "emails": {
            "total_scheduled": total_jobs,
            "sent": sent_jobs,
            "failed": failed_jobs,
            "pending": pending_jobs,
            "delivery_rate": round(sent_jobs / total_jobs * 100, 1) if total_jobs > 0 else 0,
        },
        "per_step": step_stats,
    }
