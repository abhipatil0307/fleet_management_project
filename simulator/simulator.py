import json
import os
import random
import time
from pathlib import Path

import requests


API_URL = os.getenv(
    "SIMULATOR_API_URL",
    "http://127.0.0.1:8000/api/robots/update/"
)

FLEET_SIZE = int(os.getenv("FLEET_SIZE", "8"))
UPDATE_INTERVAL = float(os.getenv("UPDATE_INTERVAL", "1"))
PAYLOAD_SIZE = os.getenv("PAYLOAD_SIZE", "small").lower()

SITE_WIDTH = 900
SITE_HEIGHT = 560

MIN_X = 10
MAX_X = SITE_WIDTH - 10
MIN_Y = 10
MAX_Y = SITE_HEIGHT - 10

ROBOTS_FILE = Path(__file__).resolve().parent.parent / "robots.json"


STATUSES = [
    "idle",
    "active",
    "on_mission",
    "charging",
]


def load_robots():
    with open(ROBOTS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    robots = []

    for i in range(FLEET_SIZE):
        if i < len(data):
            item = data[i]

            x = item["start"]["x"]
            y = item["start"]["y"]

            robot_type = item["robot_type"]

        else:
            x = random.uniform(MIN_X, MAX_X)
            y = random.uniform(MIN_Y, MAX_Y)
            robot_type = (
                "picker" if i % 2 == 0 else "hauler"
            )

        robots.append({
            "robot_id": f"r{i + 1}",
            "robot_type": robot_type,
            "x": x,
            "y": y,
            "battery": random.uniform(90, 100),
            "status": "idle",
            "dx": random.uniform(-2, 2),
            "dy": random.uniform(-2, 2),
            "charge_time": 0,
        })

    return robots


def choose_status(robot):
    battery = robot["battery"]

    if battery <= 20:
        robot["status"] = "charging"
        return

    if robot["status"] == "charging":
        if battery >= 95:
            robot["status"] = "idle"
        return

    chance = random.random()

    if chance < 0.02:
        robot["status"] = "idle"

    elif chance < 0.05:
        robot["status"] = "charging"

    elif chance < 0.45:
        robot["status"] = "active"

    else:
        robot["status"] = "on_mission"


def move_robot(robot):
    if robot["status"] == "charging":
        return

    robot["x"] += robot["dx"]
    robot["y"] += robot["dy"]

    if robot["x"] <= MIN_X or robot["x"] >= MAX_X:
        robot["dx"] *= -1

    if robot["y"] <= MIN_Y or robot["y"] >= MAX_Y:
        robot["dy"] *= -1

    robot["x"] = max(
        MIN_X,
        min(MAX_X, robot["x"])
    )

    robot["y"] = max(
        MIN_Y,
        min(MAX_Y, robot["y"])
    )

    if random.random() < 0.08:
        robot["dx"] += random.uniform(-0.5, 0.5)
        robot["dy"] += random.uniform(-0.5, 0.5)

        robot["dx"] = max(-3, min(3, robot["dx"]))
        robot["dy"] = max(-3, min(3, robot["dy"]))


def update_battery(robot):
    if robot["status"] == "charging":
        robot["battery"] += random.uniform(0.5, 1.2)
    elif robot["status"] in ["active", "on_mission"]:
        robot["battery"] -= random.uniform(0.05, 0.25)
    else:
        robot["battery"] -= random.uniform(0.01, 0.05)

    robot["battery"] = max(
        0,
        min(100, robot["battery"])
    )


def payload_padding():
    if PAYLOAD_SIZE == "large":
        return "x" * 5000

    if PAYLOAD_SIZE == "medium":
        return "x" * 1000

    return ""


def send_update(robot, elapsed):

    payload = {
        "robot_id": robot["robot_id"],
        "t": round(elapsed, 2),
        "x": round(robot["x"], 2),
        "y": round(robot["y"], 2),
        "status": robot["status"],
        "battery": round(robot["battery"], 2),
    }

    padding = payload_padding()

    if padding:
        payload["telemetry"] = padding

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=3
        )

        if response.status_code != 200:
            print(
                f"[ERROR] {robot['robot_id']} "
                f"HTTP {response.status_code}"
            )
            return False

        return True

    except requests.RequestException as error:
        print(
            f"[CONNECTION ERROR] "
            f"{robot['robot_id']}: {error}"
        )
        return False


def print_status(robots, elapsed):

    active = sum(
        r["status"] in ["active", "on_mission"]
        for r in robots
    )

    charging = sum(
        r["status"] == "charging"
        for r in robots
    )

    average_battery = (
        sum(r["battery"] for r in robots)
        / len(robots)
    )

    print(
        f"\r"
        f"t={elapsed:6.1f}s | "
        f"robots={len(robots):3} | "
        f"active={active:3} | "
        f"charging={charging:3} | "
        f"battery={average_battery:5.1f}%",
        end="",
        flush=True
    )


def main():

    robots = load_robots()

    print()
    print("========================================")
    print("      PEPPERMINT ROBOT SIMULATOR")
    print("========================================")
    print(f"API URL       : {API_URL}")
    print(f"Fleet size    : {FLEET_SIZE}")
    print(f"Update rate   : {UPDATE_INTERVAL}s")
    print(f"Payload size  : {PAYLOAD_SIZE}")
    print(f"Site          : {SITE_WIDTH} x {SITE_HEIGHT}")
    print("----------------------------------------")
    print("Press CTRL+C to stop")
    print()

    start_time = time.time()

    try:

        while True:

            elapsed = time.time() - start_time

            for robot in robots:

                choose_status(robot)

                move_robot(robot)

                update_battery(robot)

                send_update(
                    robot,
                    elapsed
                )

            print_status(
                robots,
                elapsed
            )

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:

        print("\n")
        print("Simulator stopped.")


if __name__ == "__main__":
    main()