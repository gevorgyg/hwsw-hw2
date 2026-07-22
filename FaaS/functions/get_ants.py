"""get_ants: read-only roster of every ant's id, job, and status."""

from state_store import load_event, load_state, reply


def handler(event):
    state = load_state()
    return {"ants": [{"id": int(ant_id), "job": a["caste"],
                      "status": a["status"]}
                     for ant_id, a in sorted(state["ants"].items(),
                                             key=lambda kv: int(kv[0]))]}


if __name__ == "__main__":
    reply(handler(load_event()))
