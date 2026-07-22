"""colony_status: read-only snapshot of the whole colony state."""

from state_store import CASTES, available_chambers, load_event, load_state, reply


def handler(event):
    state = load_state()
    by_caste = {caste: 0 for caste in CASTES}
    busy = 0
    for ant in state["ants"].values():
        by_caste[ant["caste"]] += 1
        if ant["status"] != "idle":
            busy += 1
    return {
        "day": state["day"],
        "food": state["food"],
        "ants": by_caste,
        "busy_ants": busy,
        "larvae": len(state["larvae"]),
        "num_chambers": state["num_chambers"],
        "num_available_chambers": available_chambers(state),
        "pending_chambers": state["pending_chambers"],
        "trails": sorted(state["trails"]),
        "expeditions_out": [
            {"id": int(expedition_id), "source": e["source"],
             "days_out": state["day"] - e["departed_day"]}
            for expedition_id, e in sorted(state["expeditions"].items(),
                                           key=lambda kv: int(kv[0]))
            if e["status"] == "out"],
    }


if __name__ == "__main__":
    reply(handler(load_event()))
