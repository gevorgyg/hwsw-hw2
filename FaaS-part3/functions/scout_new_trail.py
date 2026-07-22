from state_store import (fail, idle_ants, load, load_event, reply, require,
                         save)


def handler(event):
    source = require(event, "source")
    trails = load("trails")
    ants = load("ants")
    if source in trails:
        fail(f"trail to {source!r} already known")
    idle = idle_ants(ants, "forager")
    if not idle:
        fail("no idle forager available to scout")
    trails.append(source)
    save("trails", trails)
    return {"source": source, "scouted_by": idle[0]}


if __name__ == "__main__":
    reply(handler(load_event()))
