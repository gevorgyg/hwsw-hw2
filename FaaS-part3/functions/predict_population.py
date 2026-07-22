from state_store import count_ants, load, load_event, reply, to_int


def handler(event):
    days = to_int(event, "days")
    census = load("census")
    day = load("day")["day"]
    food = load("food")["food"]
    ants = load("ants")
    larvae = load("larvae")["items"]
    chambers = load("chambers")
    entries = sorted((int(d), c) for d, c in census.items())
    growth = 0
    if len(entries) >= 2 and entries[-1][0] > entries[0][0]:
        first_day, first = entries[0]
        last_day, last = entries[-1]
        growth = (((last["ants"] + last["larvae"])
                   - (first["ants"] + first["larvae"]))
                  // (last_day - first_day))
    current = len(ants["items"]) + len(larvae)
    caps = (("food", food),
            ("nurses", count_ants(ants, "nurse") - len(larvae)),
            ("chambers", chambers["total"] - len(larvae)))
    limiting = min(caps, key=lambda item: item[1])[0]
    forecast = [{"day": day + i, "population": current + growth * i}
                for i in range(1, days + 1)]
    return {"based_on_days": len(entries), "daily_growth": growth,
            "current_population": current, "limiting_factor": limiting,
            "forecast": forecast}


if __name__ == "__main__":
    reply(handler(load_event()))
