import json
from datetime import timedelta

from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from pathlib import Path
from .models import Robot, RobotEvent
from .services import process_robot_update


def robot_to_dict(robot):
    """
    Convert Robot model object into API response dictionary.
    """

    return {
        "robot_id": robot.robot_id,
        "robot_type": robot.robot_type,
        "x": robot.x,
        "y": robot.y,
        "battery": robot.battery,
        "status": robot.status,
        "last_seen": (
            robot.last_seen.isoformat()
            if robot.last_seen
            else None
        ),
        "updated_at": robot.updated_at.isoformat(),
    }


@require_GET
def robot_list(request):
    """
    GET /api/robots/

    Return all robots with their current state.
    """

    robots = Robot.objects.all()

    data = [
        robot_to_dict(robot)
        for robot in robots
    ]

    return JsonResponse({
        "count": len(data),
        "robots": data,
    })


@require_GET
def robot_detail(request, robot_id):
    """
    GET /api/robots/<robot_id>/

    Return one robot.
    """

    try:
        robot = Robot.objects.get(
            robot_id=robot_id
        )

    except Robot.DoesNotExist:
        return JsonResponse(
            {
                "error": "Robot not found",
                "robot_id": robot_id,
            },
            status=404,
        )

    return JsonResponse({
        "robot": robot_to_dict(robot),
    })


@csrf_exempt
@require_POST
def robot_update(request):
    """
    POST /api/robots/update/

    Receive a robot update from the simulator.
    """

    # ----------------------------------------
    # Parse JSON
    # ----------------------------------------

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400,
        )

    # ----------------------------------------
    # Validate required fields
    # ----------------------------------------

    required_fields = [
        "robot_id",
        "t",
        "x",
        "y",
        "status",
        "battery",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return JsonResponse(
            {
                "error": "Missing required fields",
                "fields": missing_fields,
            },
            status=400,
        )

    # ----------------------------------------
    # Process robot update
    # ----------------------------------------

    try:
        robot, event = process_robot_update(data)

    except Robot.DoesNotExist:
        return JsonResponse(
            {
                "error": "Robot not found",
                "robot_id": data["robot_id"],
            },
            status=404,
        )

    except (KeyError, ValueError, TypeError) as exc:
        return JsonResponse(
            {
                "error": "Invalid robot update",
                "details": str(exc),
            },
            status=400,
        )

    # ----------------------------------------
    # Broadcast live update via WebSocket
    # ----------------------------------------

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "robots",
        {
            "type": "robot_update",
            "robot": robot_to_dict(robot),
        },
    )

    # ----------------------------------------
    # Return REST API response
    # ----------------------------------------

    return JsonResponse(
        {
            "message": "Robot update processed successfully",

            "robot": robot_to_dict(robot),

            "event": {
                "timestamp": event.timestamp,
                "x": event.x,
                "y": event.y,
                "status": event.status,
                "battery": event.battery,
            },
        },
        status=200,
    )

# Dashboard code 

def dashboard(request):
    return render(request, "dashboard/index.html")

@require_GET
def robot_history(request):
    window = request.GET.get("window", "5m")

    minutes = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "1h": 60,
    }.get(window)

    if not minutes:
        return JsonResponse({"error": "Invalid window"}, status=400)

    since = timezone.now() - timedelta(minutes=minutes)

    events = RobotEvent.objects.filter(
        received_at__gte=since
    ).order_by("received_at")

    buckets = {}

    for event in events:
        # Group into 5-second buckets for short windows
        seconds = int(event.received_at.timestamp())

        bucket_size = 5 if minutes <= 5 else 30
        bucket = seconds - (seconds % bucket_size)

        buckets.setdefault(bucket, []).append(event.battery)

    points = [
        {
            "time": bucket,
            "battery": round(sum(values) / len(values), 2),
        }
        for bucket, values in sorted(buckets.items())
    ]

    return JsonResponse({
        "window": window,
        "points": points,
    })

@csrf_exempt
@require_POST
def simulator_config(request):
    try:
        data = json.loads(request.body)

        config = {
            "running": bool(data.get("running", True)),
            "fleet_size": max(1, min(100, int(data.get("fleet_size", 8)))),
            "update_interval": max(
                0.2,
                min(10, float(data.get("update_interval", 1)))
            ),
        }

        path = Path(__file__).resolve().parent.parent / "simulator_config.json"

        with open(path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)

        return JsonResponse({
            "message": "Simulator configuration updated",
            "config": config
        })

    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return JsonResponse({
            "error": "Invalid simulator configuration",
            "details": str(exc)
        }, status=400)
        