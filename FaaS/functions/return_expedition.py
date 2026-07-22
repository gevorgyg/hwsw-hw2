"""return_expedition: the party reports back with |foragers| + |days| food.

A party is away at least one night, so returning on the departure day is
refused.
"""

from state_store import (fail, load_event, load_state, reply, save_state,
                         to_int)


def handler(event):
    state = load_state()
    expedition_id = to_int(event, "id")
    expedition = state["expeditions"].get(str(expedition_id))
    if expedition is None:
        fail(f"no expedition with id {expedition_id}")
    if expedition["status"] != "out":
        fail(f"expedition {expedition_id} already {expedition['status']}")
    if state["day"] <= expedition["departed_day"]:
        fail(f"expedition {expedition_id} left today, "
             "it can return tomorrow at the earliest")
    days_out = state["day"] - expedition["departed_day"]
    gained = len(expedition["foragers"]) + days_out
    state["food"] += gained
    for ant_id in expedition["foragers"]:
        ant = state["ants"].get(str(ant_id))
        if ant is not None:
            ant["status"] = "idle"
    expedition["status"] = "returned"
    save_state(state)
    return {"expedition_id": expedition_id, "days_out": days_out,
            "food_gained": gained, "food_total": state["food"]}


if __name__ == "__main__":
    reply(handler(load_event()))
