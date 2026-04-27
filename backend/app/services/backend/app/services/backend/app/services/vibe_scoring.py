def calculate_vibe_score(signals):
    return (
        0.35 * signals.get("crowd_level", 0) +
        0.20 * signals.get("social_activity", 0) +
        0.15 * signals.get("time_pattern", 0) +
        0.10 * signals.get("live_music", 0) +
        0.10 * signals.get("user_votes", 0) +
        0.10 * signals.get("admin_boost", 0)
    )
