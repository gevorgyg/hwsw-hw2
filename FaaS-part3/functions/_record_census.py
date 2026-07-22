from state_store import load, load_event, reply, save


def handler(event):
    day = load("day")["day"]
    ants = load("ants")["items"]
    larvae = load("larvae")["items"]
    census = load("census")
    census[str(day)] = {"ants": len(ants), "larvae": len(larvae)}
    save("census", census)
    return {"recorded_day": day}


if __name__ == "__main__":
    reply(handler(load_event()))
