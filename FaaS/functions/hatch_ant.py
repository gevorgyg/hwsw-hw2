"""hatch_ant: the oldest larva matures into an idle ant of the given caste."""

from state_store import (fail, load_event, load_state, reply, save_state,
                         to_caste)


def handler(event):
    state = load_state()
    caste = to_caste(event)
    if not state["larvae"]:
        fail("no larvae to hatch")
    larva_id = min(state["larvae"])
    state["larvae"].remove(larva_id)
    ant_id = state["next_ant"]
    state["next_ant"] += 1
    state["ants"][str(ant_id)] = {"caste": caste, "status": "idle"}
    save_state(state)
    return {"ant_id": ant_id, "caste": caste, "from_larva": larva_id}


if __name__ == "__main__":
    reply(handler(load_event()))
