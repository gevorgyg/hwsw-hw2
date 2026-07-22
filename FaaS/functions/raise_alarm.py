"""raise_alarm: a threat attacks; more soldiers than threat repels it.

If the threat exceeds the soldier count the hive is overrun and the food
store and all larvae are lost. Ants away on expedition are unaffected.
"""

from state_store import count_ants, load_event, load_state, reply, save_state, to_int


def handler(event):
    state = load_state()
    threat = to_int(event, "threat")
    soldiers = count_ants(state, "soldier")
    if threat > soldiers:
        food_lost = state["food"]
        larvae_lost = len(state["larvae"])
        state["food"] = 0
        state["larvae"] = []
        save_state(state)
        return {"outcome": "overrun", "threat": threat,
                "soldiers": soldiers, "food_lost": food_lost,
                "larvae_lost": larvae_lost}
    return {"outcome": "repelled", "threat": threat, "soldiers": soldiers}


if __name__ == "__main__":
    reply(handler(load_event()))
