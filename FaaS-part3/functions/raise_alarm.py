from state_store import count_ants, emit, load, load_event, reply, save, to_int


def handler(event):
    threat = to_int(event, "threat")
    ants = load("ants")
    soldiers = count_ants(ants, "soldier")
    if threat > soldiers:
        food = load("food")
        larvae = load("larvae")
        food_lost = food["food"]
        larvae_lost = len(larvae["items"])
        food["food"] = 0
        larvae["items"] = []
        save("food", food)
        save("larvae", larvae)
        emit("population_changed")
        return {"outcome": "overrun", "threat": threat,
                "soldiers": soldiers, "food_lost": food_lost,
                "larvae_lost": larvae_lost}
    return {"outcome": "repelled", "threat": threat, "soldiers": soldiers}


if __name__ == "__main__":
    reply(handler(load_event()))
