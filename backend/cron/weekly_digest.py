"""
Weekly Performance Digest — Cron job + email builder.
Runs every Monday at 09:00 UTC.  Sends branded digest to all users:
  - Global top 5 strategies (7-day return)
  - User-specific followed-strategy performance
  - Free users see gated content with upgrade CTA
  - Pro users see full metrics
"""
import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta
import uuid

from database import db
from services.email_service import send_email, APP_URL, APP_NAME

logger = logging.getLogger("AlphaAI.WeeklyDigest")

digest_logs_col = db["weekly_digest_logs"]
digest_prefs_col = db["digest_preferences"]
strategies_col = db["strategies_mp"]
performance_col = db["strategy_performance"]
followed_col = db["followed_strategies"]
users_col = db["users"]

ADMIN_SECRET = os.environ.get("ADMIN_SECRET")


# ═══════════════════════════════════════════
#  DATA COLLECTION
# ═══════════════════════════════════════════

async def _get_top_strategies(limit: int = 5) -> list:
    """Fetch top strategies by 7-day return from strategy_performance."""
    query = {"status": "published", "is_public": True}
    cursor = strategies_col.find(query, {"_id": 0}).limit(50)
    strategies = await cursor.to_list(length=50)

    if not strategies:
        return []

    sids = [s["id"] for s in strategies]
    perf_cursor = performance_col.find(
        {"strategy_id": {"$in": sids}}, {"_id": 0}
    ).sort("uploaded_at", -1)
    all_perfs = await perf_cursor.to_list(length=200)

    perf_map = {}
    for p in all_perfs:
        sid = p["strategy_id"]
        if sid not in perf_map:
            perf_map[sid] = p

    enriched = []
    for s in strategies:
        perf = perf_map.get(s["id"], {})
        enriched.append({
            "name": s.get("name", "Unnamed"),
            "category": s.get("category", "other"),
            "total_return": perf.get("total_return", s.get("total_return", 0)) or 0,
            "win_rate": perf.get("win_rate", s.get("win_rate", 0)) or 0,
            "sharpe_ratio": perf.get("sharpe_ratio", s.get("sharpe_ratio", 0)) or 0,
            "total_trades": perf.get("total_trades", 0) or 0,
            "strategy_id": s["id"],
        })

    enriched.sort(key=lambda x: x["total_return"], reverse=True)
    return enriched[:limit]


async def _get_user_followed_performance(user_id: str) -> list:
    """Fetch performance of strategies a user follows."""
    follows = await followed_col.find(
        {"user_id": user_id}, {"_id": 0, "strategy_id": 1}
    ).to_list(50)

    if not follows:
        return []

    sids = [f["strategy_id"] for f in follows]

    # Fetch strategy names from marketplace
    strats_cursor = strategies_col.find({"id": {"$in": sids}}, {"_id": 0})
    strats = {s["id"]: s for s in await strats_cursor.to_list(50)}

    # Also check leaderboard collection for lab strategies
    lb_cursor = db.strategy_leaderboard.find({"id": {"$in": sids}}, {"_id": 0})
    lb_strats = {s["id"]: s for s in await lb_cursor.to_list(50)}

    # Fetch perf
    perf_cursor = performance_col.find(
        {"strategy_id": {"$in": sids}}, {"_id": 0}
    ).sort("uploaded_at", -1)
    all_perfs = await perf_cursor.to_list(100)
    perf_map = {}
    for p in all_perfs:
        if p["strategy_id"] not in perf_map:
            perf_map[p["strategy_id"]] = p

    result = []
    for sid in sids:
        s = strats.get(sid) or lb_strats.get(sid) or {}
        perf = perf_map.get(sid, {})
        name = s.get("name", sid[:12])
        result.append({
            "name": name,
            "total_return": perf.get("total_return", s.get("metrics", {}).get("total_return", 0)) or 0,
            "win_rate": perf.get("win_rate", s.get("metrics", {}).get("win_rate", 0)) or 0,
            "sharpe_ratio": perf.get("sharpe_ratio", s.get("metrics", {}).get("sharpe_ratio", 0)) or 0,
        })

    return result


# ═══════════════════════════════════════════
#  EMAIL TEMPLATE
# ═══════════════════════════════════════════

def _strategy_row(name: str, ret: float, wr: float, sharpe: float, rank: int) -> str:
    color = "#00FF94" if ret >= 0 else "#FF6B6B"
    return f"""<tr>
      <td style="padding:10px 12px;color:#a1a1aa;font-size:14px;border-bottom:1px solid #1e1e1e;">{rank}</td>
      <td style="padding:10px 12px;color:#e4e4e7;font-size:14px;font-weight:500;border-bottom:1px solid #1e1e1e;">{name}</td>
      <td style="padding:10px 12px;color:{color};font-size:14px;font-weight:600;border-bottom:1px solid #1e1e1e;">{ret:+.1f}%</td>
      <td style="padding:10px 12px;color:#a1a1aa;font-size:14px;border-bottom:1px solid #1e1e1e;">{wr:.0f}%</td>
      <td style="padding:10px 12px;color:#a1a1aa;font-size:14px;border-bottom:1px solid #1e1e1e;">{sharpe:.2f}</td>
    </tr>"""


def _blurred_row() -> str:
    return """<tr>
      <td colspan="5" style="padding:10px 12px;color:#52525b;font-size:14px;border-bottom:1px solid #1e1e1e;text-align:center;font-style:italic;">
        &#x2588;&#x2588;&#x2588;&#x2588; &#x2588;&#x2588;&#x2588; &#x2588;&#x2588;.&#x2588;% &#x2588;&#x2588;%
      </td>
    </tr>"""


def _table_header() -> str:
    return """<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
    <tr style="background-color:#1a1a1a;">
      <th style="padding:10px 12px;color:#71717a;font-size:12px;text-align:left;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;">#</th>
      <th style="padding:10px 12px;color:#71717a;font-size:12px;text-align:left;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;">Strategy</th>
      <th style="padding:10px 12px;color:#71717a;font-size:12px;text-align:left;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;">Return</th>
      <th style="padding:10px 12px;color:#71717a;font-size:12px;text-align:left;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;">Win Rate</th>
      <th style="padding:10px 12px;color:#71717a;font-size:12px;text-align:left;text-transform:uppercase;letter-spacing:0.08em;font-weight:500;">Sharpe</th>
    </tr>"""


def build_digest_email(
    email: str,
    user_name: str,
    is_pro: bool,
    top_strategies: list,
    followed_strategies: list,
    week_label: str,
) -> tuple:
    """Build subject + HTML for the weekly digest."""

    subject = f"Your Weekly AlphaAI Digest — {week_label}"

    # Global top strategies section
    global_rows = ""
    show_count = len(top_strategies) if is_pro else min(3, len(top_strategies))
    for i, s in enumerate(top_strategies[:show_count]):
        global_rows += _strategy_row(s["name"], s["total_return"], s["win_rate"], s["sharpe_ratio"], i + 1)
    if not is_pro and len(top_strategies) > 3:
        for _ in range(len(top_strategies) - 3):
            global_rows += _blurred_row()

    # Followed strategies section
    if followed_strategies and is_pro:
        followed_section = f"""
        <tr><td style="padding:30px 40px 10px;">
          <h2 style="color:#fff;font-size:18px;margin:0 0 4px;font-weight:600;">Your Followed Strategies</h2>
          <p style="color:#71717a;font-size:13px;margin:0;">Performance of strategies you're tracking</p>
        </td></tr>
        <tr><td style="padding:10px 40px 20px;">
          {_table_header()}
          {''.join(_strategy_row(s["name"], s["total_return"], s["win_rate"], s["sharpe_ratio"], i+1) for i, s in enumerate(followed_strategies))}
          </table>
        </td></tr>"""
    elif followed_strategies and not is_pro:
        followed_section = f"""
        <tr><td style="padding:30px 40px 10px;">
          <h2 style="color:#fff;font-size:18px;margin:0 0 4px;font-weight:600;">Your Followed Strategies</h2>
          <p style="color:#71717a;font-size:13px;margin:0 0 16px;">You follow {len(followed_strategies)} strategies</p>
          <div style="background:#1a1a1a;border:1px solid #7B61FF;border-radius:12px;padding:24px;text-align:center;">
            <p style="color:#a1a1aa;font-size:15px;margin:0 0 16px;">Upgrade to Pro to unlock your personalized weekly performance report.</p>
            <a href="{APP_URL}/pricing" style="display:inline-block;background:linear-gradient(135deg,#7B61FF,#6B51EF);color:#fff;text-decoration:none;padding:12px 28px;border-radius:50px;font-size:14px;font-weight:600;">Upgrade to Pro</a>
          </div>
        </td></tr>"""
    else:
        followed_section = f"""
        <tr><td style="padding:30px 40px 10px;">
          <h2 style="color:#fff;font-size:18px;margin:0 0 4px;font-weight:600;">Your Followed Strategies</h2>
          <p style="color:#a1a1aa;font-size:14px;margin:0 0 16px;">You're not following any strategies yet.</p>
          <a href="{APP_URL}/strategies" style="display:inline-block;background:linear-gradient(135deg,#00FF94,#00CC76);color:#000;text-decoration:none;padding:12px 28px;border-radius:50px;font-size:14px;font-weight:600;">Discover Top Strategies</a>
        </td></tr>"""

    # Upgrade banner for free users
    upgrade_banner = ""
    if not is_pro:
        upgrade_banner = f"""
        <tr><td style="padding:10px 40px 20px;">
          <div style="background:linear-gradient(135deg,rgba(123,97,255,0.15),rgba(0,255,148,0.08));border:1px solid #7B61FF;border-radius:12px;padding:20px;text-align:center;">
            <p style="color:#e4e4e7;font-size:15px;margin:0 0 12px;font-weight:500;">Get full strategy metrics, personalized reports, and real-time signals</p>
            <a href="{APP_URL}/pricing" style="display:inline-block;background:linear-gradient(135deg,#FFB800,#FF8C00);color:#000;text-decoration:none;padding:12px 28px;border-radius:50px;font-size:14px;font-weight:600;">Upgrade to Pro</a>
          </div>
        </td></tr>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#050505;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#050505;padding:40px 20px;"><tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#121212;border-radius:16px;border:1px solid #27272a;">

<!-- Header -->
<tr><td style="padding:40px 40px 20px;text-align:center;background:linear-gradient(180deg,rgba(123,97,255,0.08),transparent);border-radius:16px 16px 0 0;">
  <h1 style="color:#fff;margin:0;font-size:22px;font-weight:600;">Weekly Performance Digest</h1>
  <p style="color:#7B61FF;font-size:12px;letter-spacing:0.15em;text-transform:uppercase;margin:6px 0 0;font-weight:400;">{APP_NAME} Signal Intelligence</p>
  <p style="color:#71717a;font-size:13px;margin:8px 0 0;">{week_label}</p>
</td></tr>

<!-- Greeting -->
<tr><td style="padding:20px 40px 10px;">
  <p style="color:#a1a1aa;font-size:15px;margin:0;">Hi {user_name},</p>
  <p style="color:#a1a1aa;font-size:15px;margin:6px 0 0;">Here's your weekly strategy performance summary.</p>
</td></tr>

<!-- Global Top Strategies -->
<tr><td style="padding:20px 40px 10px;">
  <h2 style="color:#fff;font-size:18px;margin:0 0 4px;font-weight:600;">Top Performing Strategies</h2>
  <p style="color:#71717a;font-size:13px;margin:0;">Global leaderboard — ranked by return</p>
</td></tr>
<tr><td style="padding:10px 40px 20px;">
  {_table_header()}
  {global_rows}
  </table>
</td></tr>

{followed_section}

{upgrade_banner}

<!-- CTA -->
<tr><td style="padding:20px 40px 30px;text-align:center;">
  <a href="{APP_URL}/dashboard" style="display:inline-block;background:linear-gradient(135deg,#7B61FF,#6B51EF);color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:15px;font-weight:600;">View Dashboard</a>
  <span style="display:inline-block;width:12px;"></span>
  <a href="{APP_URL}/strategies" style="display:inline-block;color:#7B61FF;text-decoration:none;padding:14px 20px;font-size:14px;font-weight:500;">View Leaderboard &rarr;</a>
</td></tr>

<!-- Footer -->
<tr><td style="padding:20px 40px;border-top:1px solid #27272a;">
  <p style="color:#52525b;font-size:11px;margin:0;text-align:center;">
    You're receiving this because you have an {APP_NAME} account.
    <br><a href="{APP_URL}/api/digest/unsubscribe?email={email}" style="color:#52525b;text-decoration:underline;">Unsubscribe from weekly digest</a>
  </p>
</td></tr>

</table></td></tr></table></body></html>"""

    return subject, html


# ═══════════════════════════════════════════
#  SCHEDULER
# ═══════════════════════════════════════════

_digest_running = False
_last_digest_week = None


def _is_pro_user(user: dict) -> bool:
    tier = user.get("user_tier", "free")
    if tier in ("pro", "elite"):
        return True
    return user.get("is_pro", False) or user.get("is_elite", False)


async def _send_digest_to_user(user: dict, top_strategies: list):
    """Build and send digest to a single user."""
    email = user.get("email")
    if not email:
        return None

    user_id = user.get("id")
    user_name = user.get("name", email.split("@")[0])
    pro = _is_pro_user(user)

    # Check unsubscribe
    pref = await digest_prefs_col.find_one({"email": email.lower()})
    if pref and pref.get("unsubscribed"):
        return None

    followed = await _get_user_followed_performance(user_id)

    now = datetime.now(timezone.utc)
    week_end = now.date()
    week_start = week_end - timedelta(days=7)
    week_label = f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"

    subject, html = build_digest_email(
        email=email,
        user_name=user_name,
        is_pro=pro,
        top_strategies=top_strategies,
        followed_strategies=followed,
        week_label=week_label,
    )

    result = await send_email(email, subject, html)

    # Log delivery
    log = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "email": email,
        "is_pro": pro,
        "strategy_count": len(followed),
        "top_strategy_count": len(top_strategies),
        "status": result.get("status", "error"),
        "error": result.get("error"),
        "sent_at": now.isoformat(),
        "week_label": week_label,
    }
    await digest_logs_col.insert_one(log)

    return result


async def run_weekly_digest():
    """Send digest to all eligible users. Called by scheduler on Monday 09:00 UTC."""
    logger.info("Starting weekly digest run...")

    top_strategies = await _get_top_strategies(5)
    if not top_strategies:
        logger.warning("No published strategies found — skipping digest")
        return {"sent": 0, "skipped": 0, "errors": 0}

    # Fetch all users with valid emails (bounded to 5000)
    cursor = users_col.find(
        {"email": {"$exists": True, "$ne": ""}},
        {"_id": 0, "id": 1, "email": 1, "name": 1, "user_tier": 1, "is_pro": 1, "is_elite": 1}
    ).limit(5000)
    users = await cursor.to_list(5000)

    sent = 0
    skipped = 0
    errors = 0

    for user in users:
        try:
            result = await _send_digest_to_user(user, top_strategies)
            if result is None:
                skipped += 1
            elif result.get("status") == "sent":
                sent += 1
            elif result.get("status") == "logged":
                sent += 1  # Counts as "sent" in log-only mode
            else:
                errors += 1
        except Exception as e:
            logger.error(f"Digest error for {user.get('email')}: {e}")
            errors += 1

        # Small delay to avoid rate limits
        await asyncio.sleep(0.2)

    logger.info(f"Weekly digest complete: sent={sent}, skipped={skipped}, errors={errors}")
    return {"sent": sent, "skipped": skipped, "errors": errors}


async def start_weekly_digest_scheduler():
    """Background loop — fires run_weekly_digest every Monday at 09:00 UTC."""
    global _digest_running, _last_digest_week
    if _digest_running:
        return
    _digest_running = True
    logger.info("Weekly digest scheduler started")

    while True:
        try:
            now = datetime.now(timezone.utc)
            # Monday = weekday 0, 09:00 UTC
            is_monday = now.weekday() == 0
            is_9am_window = now.hour == 9 and now.minute < 5
            current_week = now.isocalendar()[1]

            if is_monday and is_9am_window and _last_digest_week != current_week:
                _last_digest_week = current_week
                await run_weekly_digest()
        except Exception as e:
            logger.error(f"Digest scheduler error: {e}")

        await asyncio.sleep(60)  # Check every 60 seconds
