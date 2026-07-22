from state_store import load, load_event, reply


def handler(event):
    ants = load("ants")
    return {"ants": [{"id": int(ant_id), "job": a["caste"],
                      "status": a["status"]}
                     for ant_id, a in sorted(ants["items"].items(),
                                             key=lambda kv: int(kv[0]))]}


if __name__ == "__main__":
    reply(handler(load_event()))
