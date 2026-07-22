"""new_day: advance the clock and open the chambers dug the day before."""

from state_store import load_event, load_state, reply, save_state


def handler(event):
    state = load_state()
    state["day"] += 1
    opened = state["pending_chambers"]
    state["num_chambers"] += opened
    state["pending_chambers"] = 0
    save_state(state)
    return {"day": state["day"], "chambers_opened": opened}


if __name__ == "__main__":
    reply(handler(load_event()))
