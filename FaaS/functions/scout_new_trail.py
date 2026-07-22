"""scout_new_trail: an idle forager marks a route to a new food source."""

from state_store import (fail, idle_ants, load_event, load_state, reply,
                         require, save_state)


def handler(event):
    state = load_state()
    source = require(event, "source")
    if source in state["trails"]:
        fail(f"trail to {source!r} already known")
    idle = idle_ants(state, "forager")
    if not idle:
        fail("no idle forager available to scout")
    state["trails"].append(source)
    save_state(state)
    return {"source": source, "scouted_by": idle[0]}


if __name__ == "__main__":
    reply(handler(load_event()))
