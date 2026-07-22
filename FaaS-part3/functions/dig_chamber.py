from state_store import fail, idle_ants, load, load_event, reply, save


def handler(event):
    ants = load("ants")
    food = load("food")
    chambers = load("chambers")
    idle = len(idle_ants(ants, "worker"))
    if idle == 0:
        fail("no idle workers to dig")
    crew = min(idle, food["food"])
    if crew == 0:
        fail(f"cannot provision any digger, "
             f"only {food['food']} food in stores")
    food["food"] -= crew
    chambers["pending"] += crew
    save("food", food)
    save("chambers", chambers)
    return {"chambers_started": crew, "workers_digging": crew,
            "food_spent": crew}


if __name__ == "__main__":
    reply(handler(load_event()))
