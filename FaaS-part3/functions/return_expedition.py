from state_store import fail, load, load_event, reply, save, to_int


def handler(event):
    expedition_id = to_int(event, "id")
    expeditions = load("expeditions")
    day = load("day")["day"]
    expedition = expeditions["items"].get(str(expedition_id))
    if expedition is None:
        fail(f"no expedition with id {expedition_id}")
    if expedition["status"] != "out":
        fail(f"expedition {expedition_id} already {expedition['status']}")
    if day <= expedition["departed_day"]:
        fail(f"expedition {expedition_id} left today, "
             "it can return tomorrow at the earliest")
    food = load("food")
    ants = load("ants")
    days_out = day - expedition["departed_day"]
    gained = len(expedition["foragers"]) + days_out
    food["food"] += gained
    for ant_id in expedition["foragers"]:
        ant = ants["items"].get(str(ant_id))
        if ant is not None:
            ant["status"] = "idle"
    expedition["status"] = "returned"
    save("food", food)
    save("ants", ants)
    save("expeditions", expeditions)
    return {"expedition_id": expedition_id, "days_out": days_out,
            "food_gained": gained, "food_total": food["food"]}


if __name__ == "__main__":
    reply(handler(load_event()))
