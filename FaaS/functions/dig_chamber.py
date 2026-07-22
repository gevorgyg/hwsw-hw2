"""dig_chamber: every idle worker digs one chamber for one food.

The crew is capped by what the stores can provision, and the chambers
open on the next day.
"""

from state_store import fail, idle_ants, load_event, load_state, reply, save_state


def handler(event):
    state = load_state()
    idle = len(idle_ants(state, "worker"))
    if idle == 0:
        fail("no idle workers to dig")
    crew = min(idle, state["food"])
    if crew == 0:
        fail(f"cannot provision any digger, "
             f"only {state['food']} food in stores")
    state["food"] -= crew
    state["pending_chambers"] += crew
    save_state(state)
    return {"chambers_started": crew, "workers_digging": crew,
            "food_spent": crew}


if __name__ == "__main__":
    reply(handler(load_event()))
