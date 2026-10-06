from django.contrib import admin
from django.urls import path

from robots.views import (
    dashboard,
    robot_list,
    robot_detail,
    robot_update,
    robot_history,
    simulator_config,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("admin/", admin.site.urls),

    path("api/robots/", robot_list, name="robot-list"),

    path(
        "api/robots/update/",
        robot_update,
        name="robot-update",
    ),

    path(
        "api/robots/history/",
        robot_history,
        name="robot-history",
    ),

    path(
        "api/simulator/config/",
        simulator_config,
        name="simulator-config",
    ),

    path(
        "api/robots/<str:robot_id>/",
        robot_detail,
        name="robot-detail",
    ),
]