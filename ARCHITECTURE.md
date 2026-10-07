# Fleet Management Dashboard — Architecture

## 1. System Overview

The Fleet Management Dashboard is a Django-based real-time fleet monitoring application.

The system consists of:

- Robot Simulator
- Django Backend
- REST APIs
- Service Layer
- Database
- Django Channels / WebSocket
- Web Dashboard
- Battery History and Analytics

The simulator continuously generates robot telemetry such as:

- Robot ID
- Robot type
- X coordinate
- Y coordinate
- Battery percentage
- Robot status
- Timestamp

The backend receives this telemetry, updates the current robot state, stores historical events, and broadcasts live updates to connected dashboard clients.

---

## 2. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │   Robot Simulator     │
                         │                      │
                         │ robots.json          │
                         │ Movement              │
                         │ Battery               │
                         │ Status                │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP POST
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │       Django Backend         │
                    │                              │
                    │ /api/robots/update/          │
                    │                              │
                    │ robots/views.py              │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │       Service Layer          │
                    │                              │
                    │ robots/services.py            │
                    │                              │
                    │ process_robot_update()        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │   Robot Model    │          │ RobotEvent Model │
          │                  │          │                  │
          │ Current State    │          │ Historical Data  │
          │ Position         │          │ Battery          │
          │ Battery          │          │ Position         │
          │ Status           │          │ Status           │
          └──────────────────┘          └──────────────────┘
                    │
                    │
                    ▼
          ┌──────────────────────┐
          │ Django Channels      │
          │ WebSocket            │
          │                      │
          │ /ws/robots/          │
          └──────────┬───────────┘
                     │
                     │ Real-time JSON
                     ▼
          ┌────────────────────────────┐
          │      Web Dashboard         │
          │                            │
          │ Live Map                   │
          │ KPI Cards                  │
          │ Fleet Table                │
          │ Inspector                  │
          │ Attention Center           │
          │ Live Activity              │
          │ Battery Trend              │
          └────────────────────────────┘

## project Structure 
fleet_management/
│
├── fleet_management/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── robots/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   ├── urls.py
│   └── migrations/
│
├── simulator/
│   └── simulator.py
│
├── templates/
│   └── dashboard/
│       └── index.html
│
├── static/
│   └── images/
│       └── layout.png
│
├── robots.json
├── simulator_config.json
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── ARCHITECTURE.md
└── FINDINGS.md