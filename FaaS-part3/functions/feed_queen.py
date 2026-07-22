from state_store import (count_ants, emit, fail, load, load_event, reply,
                         save, to_int)


def handler(event):
    amount = to_int(event, "amount")
    food = load("food")
    ants = load("ants")
    larvae = load("larvae")
    chambers = load("chambers")
    if amount > food["food"]:
        fail(f"need {amount} food, only {food['food']} in stores")
    nurse_slots = count_ants(ants, "nurse") - len(larvae["items"])
    if amount > nurse_slots:
        fail(f"the queen lays one larva per food eaten, "
             f"but nurses can cover only {nurse_slots} more")
    available = chambers["total"] - len(larvae["items"])
    if amount > available:
        fail(f"the queen lays one larva per food eaten, "
             f"but only {available} chambers are available")
    food["food"] -= amount
    for _ in range(amount):
        larvae["items"].append(larvae["next"])
        larvae["next"] += 1
    save("food", food)
    save("larvae", larvae)
    emit("population_changed")
    return {"consumed": amount, "larvae_laid": amount,
            "food_left": food["food"]}


if __name__ == "__main__":
    reply(handler(load_event()))
