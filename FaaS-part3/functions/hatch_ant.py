from state_store import emit, fail, load, load_event, reply, save, to_caste


def handler(event):
    caste = to_caste(event)
    larvae = load("larvae")
    ants = load("ants")
    if not larvae["items"]:
        fail("no larvae to hatch")
    larva_id = min(larvae["items"])
    larvae["items"].remove(larva_id)
    ant_id = ants["next"]
    ants["next"] += 1
    ants["items"][str(ant_id)] = {"caste": caste, "status": "idle"}
    save("larvae", larvae)
    save("ants", ants)
    emit("population_changed")
    return {"ant_id": ant_id, "caste": caste, "from_larva": larva_id}


if __name__ == "__main__":
    reply(handler(load_event()))
