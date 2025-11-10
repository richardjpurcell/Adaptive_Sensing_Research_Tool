import json, os, pathlib
root = pathlib.Path(__file__).resolve().parents[1]  # repo root
mn = root / "data" / "manifests"
mn.mkdir(parents=True, exist_ok=True)

env = {"name":"E0-flat","grid":{"H":60,"W":80,"cell_m":250},"wind":{"speed":4,"dir_deg":210},"seed":0,"env_id":"env_e0_flat"}
fire = {"name":"single-center","ignitions":{"k":1,"placement":"center"},"model":{"family":"baseline"},"seed":0,"fire_id":"fire_single_center"}
sensors = {"name":"fleet-8","fleet":{"N":8,"groups":["ground"]},"seed":0,"sensors_id":"sensors_fleet8"}

for fname, obj in [("env_e0_flat.json",env),("fire_single_center.json",fire),("sensors_fleet8.json",sensors)]:
    with open(mn/fname, "w") as f: json.dump(obj, f, indent=2)
print(f"Wrote manifests to {mn}")
