def calculate_reward(group_size):
    if group_size >= 5:
        return {"tier": "free_drink", "tokens": 50}
    elif group_size >= 3:
        return {"tier": "boost", "tokens": 20}
    else:
        return {"tier": "base", "tokens": 10}
