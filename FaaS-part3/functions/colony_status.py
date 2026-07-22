from state_store import CASTES, load, load_event, reply


def handler(event):
    day = load("day")["day"]
    food = load("food")["food"]
    ants = load("ants")["items"]
    larvae = load("larvae")["items"]
    chambers = load("chambers")
    trails = load("trails")
    expeditions = load("expeditions")["items"]
    by_caste = {caste: 0 for caste in CASTES}
    busy = 0
    for ant in ants.values():
        by_caste[ant["caste"]] += 1
        if ant["status"] != "idle":
            busy += 1
    return {
        "day": day,
        "food": food,
        "ants": by_caste,
        "busy_ants": busy,
        "larvae": len(larvae),
        "num_chambers": chambers["total"],
        "num_available_chambers": chambers["total"] - len(larvae),
        "pending_chambers": chambers["pending"],
        "trails": sorted(trails),
        "expeditions_out": [
            {"id": int(expedition_id), "source": e["source"],
             "days_out": day - e["departed_day"]}
            for expedition_id, e in sorted(expeditions.items(),
                                           key=lambda kv: int(kv[0]))
            if e["status"] == "out"],
    }


if __name__ == "__main__":
    reply(handler(load_event()))
