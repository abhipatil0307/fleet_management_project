import json
from pathlib import Path

from django.core.management.base import BaseCommand
from robots.models import Robot


class Command(BaseCommand):
    help = "Seed robots from robots.json"

    def handle(self, *args, **options):

        file_path = Path("robots.json")

        if not file_path.exists():
            self.stdout.write(
                self.style.ERROR("robots.json not found.")
            )
            return

        with open(file_path, "r", encoding="utf-8") as file:
            robots = json.load(file)

        for data in robots:
            start = data["start"]

            robot, created = Robot.objects.update_or_create(
                robot_id=data["robot_id"],
                defaults={
                    "robot_type": data["robot_type"],
                    "x": start["x"],
                    "y": start["y"],
                    "battery": 100,
                    "status": Robot.Status.IDLE,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {robot.robot_id}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated {robot.robot_id}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully loaded {len(robots)} robots."
            )
        )