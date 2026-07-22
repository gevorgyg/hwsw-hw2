"""feed_queen: the queen eats N food and lays exactly N larvae.

All relations are 1:1, so the command is refused unless the stores hold
N food, N nurses are free of larvae, and N chambers are available.
"""

from state_store import (available_chambers, count_ants, fail, load_event,
                         load_state, reply, save_state, to_int)


def handler(event):
    state = load_state()
    amount = to_int(event, "amount")
    if amount > state["food"]:
        fail(f"need {amount} food, only {state['food']} in stores")
    nurse_slots = count_ants(state, "nurse") - len(state["larvae"])
    if amount > nurse_slots:
        fail(f"the queen lays one larva per food eaten, "
             f"but nurses can cover only {nurse_slots} more")
    available = available_chambers(state)
    if amount > available:
        fail(f"the queen lays one larva per food eaten, "
             f"but only {available} chambers are available")
    state["food"] -= amount
    for _ in range(amount):
        state["larvae"].append(state["next_larva"])
        state["next_larva"] += 1
    save_state(state)
    return {"consumed": amount, "larvae_laid": amount,
            "food_left": state["food"]}


if __name__ == "__main__":
    reply(handler(load_event()))
