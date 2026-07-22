from state_store import emit, load, load_event, reply, save


def handler(event):
    day = load("day")
    chambers = load("chambers")
    day["day"] += 1
    opened = chambers["pending"]
    chambers["total"] += opened
    chambers["pending"] = 0
    save("day", day)
    save("chambers", chambers)
    emit("population_changed")
    return {"day": day["day"], "chambers_opened": opened}


if __name__ == "__main__":
    reply(handler(load_event()))
