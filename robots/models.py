from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Robot(models.Model):

    class RobotType(models.TextChoices):
        PICKER = "picker", "Picker"
        HAULER = "hauler", "Hauler"

    class Status(models.TextChoices):
        IDLE = "idle", "Idle"
        ACTIVE = "active", "Active"
        ON_MISSION = "on_mission", "On Mission"
        CHARGING = "charging", "Charging"
        BLOCKED = "blocked", "Blocked"
        ERROR = "error", "Error"
        MAINTENANCE = "maintenance", "Maintenance"
        OFFLINE = "offline", "Offline"

    robot_id = models.CharField(
        max_length=50,
        unique=True
    )

    robot_type = models.CharField(
        max_length=20,
        choices=RobotType.choices
    )

    x = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(900),
        ]
    )

    y = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(560),
        ]
    )

    battery = models.FloatField(
        default=100,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDLE
    )

    last_seen = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["robot_id"]

    def __str__(self):
        return f"{self.robot_id} - {self.robot_type}"


class RobotEvent(models.Model):

    robot = models.ForeignKey(
        Robot,
        on_delete=models.CASCADE,
        related_name="events"
    )

    # Simulator timestamp: 0–900 seconds
    timestamp = models.FloatField()

    x = models.FloatField()

    y = models.FloatField()

    battery = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )

    status = models.CharField(
        max_length=20,
        choices=Robot.Status.choices
    )

    task_event = models.CharField(
        max_length=30,
        null=True,
        blank=True
    )

    received_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["timestamp"]

        indexes = [
            models.Index(
                fields=["robot", "timestamp"]
            ),
            models.Index(
                fields=["status", "timestamp"]
            ),
        ]

    def __str__(self):
        return f"{self.robot.robot_id} @ {self.timestamp}s"