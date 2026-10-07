# Peppermint Robotics Fleet Management Dashboard

A full-stack real-time fleet management system built for the **Peppermint Robotics SDE-1 hiring challenge**.

The application simulates warehouse robots, sends their telemetry to a Django backend, stores the latest fleet state and historical events, broadcasts live updates through WebSockets, and displays the fleet through an interactive browser dashboard.

---

# 1. Project Overview

The system contains three main parts:

1. **Robot Simulator**
   - Simulates multiple warehouse robots.
   - Generates continuous robot movement.
   - Simulates battery levels.
   - Simulates robot operating statuses.
   - Sends telemetry to the backend.

2. **Django Backend**
   - Receives robot telemetry.
   - Maintains the current state of every robot.
   - Stores robot telemetry history.
   - Provides REST/JSON APIs.
   - Provides historical battery data.
   - Broadcasts live updates through Django Channels/WebSockets.

3. **Fleet Dashboard**
   - Displays the warehouse layout.
   - Displays live robot positions.
   - Shows fleet KPIs.
   - Shows robot status and battery.
   - Provides robot search and filtering.
   - Provides robot details/inspector.
   - Displays robots requiring attention.
   - Displays live activity.
   - Displays battery trends over time.
   - Automatically reconnects the WebSocket when disconnected.

---

# 2. System Architecture

```text
                         +----------------------+
                         |    robots.json       |
                         | Initial Robot Data   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |   Robot Simulator    |
                         | simulator.py         |
                         +----------+-----------+
                                    |
                                    | HTTP POST
                                    | Robot Telemetry
                                    v
                    +--------------------------------+
                    |        Django Backend          |
                    |                                |
                    | /api/robots/update/            |
                    +---------------+----------------+
                                    |
                    +---------------+----------------+
                    |                                |
                    v                                v
          +-------------------+            +--------------------+
          | Robot             |            | RobotEvent         |
          | Current State     |            | History            |
          +-------------------+            +--------------------+
                    |                                |
                    +---------------+----------------+
                                    |
                                    v
                         +----------------------+
                         | Django Channels      |
                         | WebSocket            |
                         | /ws/robots/          |
                         +----------+-----------+
                                    |
                                    | Live Updates
                                    v
                         +----------------------+
                         | Fleet Dashboard      |
                         | Browser              |
                         +----------------------+