"""requalify_ant: retrain an idle ant for another profession.

Refused for a busy ant, and refused for a nurse whose retraining would
leave more larvae than the remaining nurses can cover (one nurse per
larva).
"""

from state_store import (count_ants, fail, load_event, load_state, reply,
                         save_state, to_caste, to_int)


def handler(event):
    state = load_state()
    ant_id = to_int(event, "id")
    profession = to_caste(event, key="profession")
    ant = state["ants"].get(str(ant_id))
    if ant is None:
        fail(f"no ant with id {ant_id}")
    if ant["status"] != "idle":
        fail(f"ant {ant_id} is busy ({ant['status']})")
    if ant["caste"] == "nurse" and profession != "nurse":
        remaining = count_ants(state, "nurse") - 1
        if len(state["larvae"]) > remaining:
            fail(f"cannot release nurse {ant_id}: {len(state['larvae'])} "
                 f"larvae need care, remaining nurses cover only {remaining}")
    previous = ant["caste"]
    ant["caste"] = profession
    save_state(state)
    return {"ant_id": ant_id, "from": previous, "to": profession}


if __name__ == "__main__":
    reply(handler(load_event()))
