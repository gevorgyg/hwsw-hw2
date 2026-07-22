from state_store import (fail, idle_ants, load, load_event, reply, require,
                         save, to_int)


def handler(event):
    source = require(event, "source")
    count = to_int(event, "count")
    trails = load("trails")
    ants = load("ants")
    day = load("day")["day"]
    expeditions = load("expeditions")
    if source not in trails:
        fail(f"no known trail to {source!r}")
    idle = idle_ants(ants, "forager")
    if len(idle) < count:
        fail(f"need {count} foragers, only {len(idle)} idle")
    party = idle[:count]
    for ant_id in party:
        ants["items"][str(ant_id)]["status"] = "foraging"
    expedition_id = expeditions["next"]
    expeditions["next"] += 1
    expeditions["items"][str(expedition_id)] = {
        "source": source,
        "foragers": party,
        "departed_day": day,
        "status": "out",
    }
    save("ants", ants)
    save("expeditions", expeditions)
    return {"expedition_id": expedition_id, "source": source,
            "foragers": party, "departed_day": day}


if __name__ == "__main__":
    reply(handler(load_event()))
