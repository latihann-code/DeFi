import json
with open("predator_state.json", "w") as f:
    json.dump({"capital": 38.100515, "current_chain": "base", "last_update": "2026-04-25T12:00:00", "current_pool": None}, f)
print("State reset to $38.10, Pool cleared to force re-deposit.")
