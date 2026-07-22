"""dispatch_foraging_party: send N idle foragers down a known trail."""

from state_store import (fail, idle_ants, load_event, load_state, reply,
                         require, save_state, to_int)


def handler(event):
    state = load_state()
    source = require(event, "source")
    count = to_int(event, "count")
    if source not in state["trails"]:
        fail(f"no known trail to {source!r}")
    idle = idle_ants(state, "forager")
    if len(idle) < count:
        fail(f"need {count} foragers, only {len(idle)} idle")
    party = idle[:count]
    for ant_id in party:
        state["ants"][str(ant_id)]["status"] = "foraging"
    expedition_id = state["next_expedition"]
    state["next_expedition"] += 1
    state["expeditions"][str(expedition_id)] = {
        "source": source,
        "foragers": party,
        "departed_day": state["day"],
        "status": "out",
    }
    save_state(state)
    return {"expedition_id": expedition_id, "source": source,
            "foragers": party, "departed_day": state["day"]}


if __name__ == "__main__":
    reply(handler(load_event()))
