from django.utils import timezone

from .models import Robot, RobotEvent


def process_robot_update(data):
    """
    Process a single robot update.

    Expected data:
    {
        "robot_id": "r1",
        "t": 12.5,
        "x": 580.2,
        "y": 35.7,
        "status": "active",
        "battery": 98.4
    }
    """

    robot_id = data["robot_id"]

    robot = Robot.objects.get(robot_id=robot_id)

    robot.x = data["x"]
    robot.y = data["y"]
    robot.status = data["status"]
    robot.battery = data["battery"]
    robot.last_seen = timezone.now()

    robot.save(
        update_fields=[
            "x",
            "y",
            "status",
            "battery",
            "last_seen",
            "updated_at",
        ]
    )

    event = RobotEvent.objects.create(
        robot=robot,
        timestamp=data["t"],
        x=data["x"],
        y=data["y"],
        status=data["status"],
        battery=data["battery"],
    )

    return robot, event