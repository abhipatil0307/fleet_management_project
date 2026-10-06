import json
import random
import time
import urllib.request

from django.core.management.base import BaseCommand
from robots.models import Robot


class Command(BaseCommand):
    help = "Run the live robot fleet simulator"

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=float, default=1)
        parser.add_argument("--fleet-size", type=int, default=8)
        parser.add_argument("--payload-size", type=int, default=0)
        parser.add_argument("--url", default="http://127.0.0.1:8000/api/robots/update/")

    def handle(self, *args, **options):
        interval = options["interval"]
        fleet_size = options["fleet_size"]
        payload_size = options["payload_size"]
        url = options["url"]

        robots = list(Robot.objects.all()[:fleet_size])

        if not robots:
            self.stdout.write(self.style.ERROR("No robots found. Run seed_robots first."))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Simulator started: {len(robots)} robots, {interval}s interval"
            )
        )

        directions = {
            r.robot_id: random.uniform(0, 6.28)
            for r in robots
        }

        t = 0

        try:
            while True:
                for robot in robots:
                    status = robot.status

                    if robot.battery < 20:
                        status = "charging"
                    elif status == "charging" and robot.battery > 95:
                        status = random.choice(["idle", "active", "on_mission"])
                    elif random.random() < 0.04:
                        status = random.choice(
                            ["idle", "active", "on_mission", "blocked"]
                        )

                    if status in ["active", "on_mission"]:
                        directions[robot.robot_id] += random.uniform(-0.4, 0.4)

                        robot.x += random.uniform(2, 7) * \
                            (1 if random.random() > 0.5 else -1)
                        robot.y += random.uniform(2, 5) * \
                            (1 if random.random() > 0.5 else -1)

                        robot.battery -= random.uniform(0.1, 0.5)

                    elif status == "charging":
                        robot.battery += random.uniform(1.0, 2.0)

                    robot.x = max(10, min(810, robot.x))
                    robot.y = max(10, min(340, robot.y))
                    robot.battery = max(0, min(100, robot.battery))

                    payload = {
                        "robot_id": robot.robot_id,
                        "t": round(t, 1),
                        "x": round(robot.x, 2),
                        "y": round(robot.y, 2),
                        "status": status,
                        "battery": round(robot.battery, 2),
                    }

                    if payload_size:
                        payload["padding"] = "x" * payload_size

                    request = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )

                    try:
                        with urllib.request.urlopen(request, timeout=3):
                            pass
                    except Exception as exc:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{robot.robot_id}: {exc}"
                            )
                        )

                t += interval
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS("Simulator stopped.")
            )