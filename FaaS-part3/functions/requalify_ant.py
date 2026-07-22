from state_store import (count_ants, fail, load, load_event, reply, save,
                         to_caste, to_int)


def handler(event):
    ant_id = to_int(event, "id")
    profession = to_caste(event, key="profession")
    ants = load("ants")
    larvae = load("larvae")
    ant = ants["items"].get(str(ant_id))
    if ant is None:
        fail(f"no ant with id {ant_id}")
    if ant["status"] != "idle":
        fail(f"ant {ant_id} is busy ({ant['status']})")
    if ant["caste"] == "nurse" and profession != "nurse":
        remaining = count_ants(ants, "nurse") - 1
        if len(larvae["items"]) > remaining:
            fail(f"cannot release nurse {ant_id}: {len(larvae['items'])} "
                 f"larvae need care, remaining nurses cover only {remaining}")
    previous = ant["caste"]
    ant["caste"] = profession
    save("ants", ants)
    return {"ant_id": ant_id, "from": previous, "to": profession}


if __name__ == "__main__":
    reply(handler(load_event()))
