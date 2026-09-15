"""
Scenario-based AI Infrastructure Agent tests.

All Kubernetes interactions are mocked. No Kubernetes cluster is required.
"""

from app.agent import nodes
from app.agent.graph import infra_graph


def test_scenario_crashloop_with_database_failure(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pod",
        lambda namespace, pod_name: {
            "success": True,
            "pod": {
                "name": pod_name,
                "namespace": namespace,
                "phase": "Running",
                "container_statuses": [
                    {
                        "name": "app",
                        "ready": False,
                        "restart_count": 8,
                        "state": {
                            "waiting": {
                                "reason": "CrashLoopBackOff"
                            }
                        },
                    }
                ],
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_logs",
        lambda namespace, pod_name: {
            "success": True,
            "logs": "Connection refused to postgres:5432",
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_events",
        lambda namespace, pod_name: {
            "success": True,
            "events": [
                {
                    "type": "Warning",
                    "reason": "BackOff",
                    "message": "Back-off restarting failed container",
                }
            ],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": (
                "Why is my pod employment-management "
                "in CrashLoopBackOff?"
            ),
            "namespace": "employment-management",
            "resource_name": "employment-management",
        }
    )

    assert result["resource_type"] == "pod"
    assert "CrashLoopBackOff" in result["symptoms"]
    assert result["logs"]
    assert result["events"]
    assert result["confidence"] == 0.65
    assert result["recommended_commands"]


def test_scenario_oomkilled(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pod",
        lambda namespace, pod_name: {
            "success": True,
            "pod": {
                "name": pod_name,
                "namespace": namespace,
                "phase": "Failed",
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_logs",
        lambda namespace, pod_name: {
            "success": True,
            "logs": "Application terminated unexpectedly",
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_events",
        lambda namespace, pod_name: {
            "success": True,
            "events": [],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": "Why was my pod OOMKilled?",
            "namespace": "default",
            "resource_name": "memory-hungry-pod",
        }
    )

    assert result["resource_type"] == "pod"
    assert "OOMKilled" in result["symptoms"]
    assert result["confidence"] == 0.85
    assert any(
        "memory" in item.lower()
        for item in result["recommendations"]
    )


def test_scenario_pending_pod(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pod",
        lambda namespace, pod_name: {
            "success": True,
            "pod": {
                "name": pod_name,
                "namespace": namespace,
                "phase": "Pending",
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_logs",
        lambda namespace, pod_name: {
            "success": True,
            "logs": "",
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_events",
        lambda namespace, pod_name: {
            "success": True,
            "events": [
                {
                    "type": "Warning",
                    "reason": "FailedScheduling",
                    "message": "Insufficient memory",
                }
            ],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": "Why is my pod Pending?",
            "namespace": "default",
            "resource_name": "pending-pod",
        }
    )

    assert result["resource_type"] == "pod"
    assert "Pending" in result["symptoms"]
    assert result["confidence"] == 0.70
    assert any(
        "node" in item.lower()
        for item in result["recommendations"]
    )


def test_scenario_image_pull_backoff(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pod",
        lambda namespace, pod_name: {
            "success": True,
            "pod": {
                "name": pod_name,
                "namespace": namespace,
                "phase": "Pending",
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_logs",
        lambda namespace, pod_name: {
            "success": True,
            "logs": "",
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_events",
        lambda namespace, pod_name: {
            "success": True,
            "events": [
                {
                    "type": "Warning",
                    "reason": "Failed",
                    "message": "Failed to pull image",
                }
            ],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": "Pod has ImagePullBackOff",
            "namespace": "default",
            "resource_name": "bad-image-pod",
        }
    )

    assert "ImagePullBackOff" in result["symptoms"]
    assert result["confidence"] == 0.85
    assert any(
        "image" in item.lower()
        for item in result["recommendations"]
    )


def test_scenario_service_connection_refused_no_endpoints(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_service",
        lambda namespace, service_name: {
            "success": True,
            "service": {
                "name": service_name,
                "namespace": namespace,
                "type": "ClusterIP",
                "selector": {"app": "backend"},
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_endpoints",
        lambda namespace, service_name: {
            "success": True,
            "ready_endpoint_count": 0,
            "not_ready_endpoint_count": 0,
            "ready_endpoints": [],
            "not_ready_endpoints": [],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": (
                "Why is my service connection refused?"
            ),
            "namespace": "default",
            "resource_name": "backend-service",
        }
    )

    assert result["resource_type"] == "service"
    assert "connection refused" in result["symptoms"]
    assert result["confidence"] == 0.75
    assert result["observations"]
    assert result["recommended_commands"]


def test_scenario_gateway_not_programmed(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "inspect_gateway",
        lambda namespace, gateway_name: {
            "success": True,
            "gateway": {
                "name": gateway_name,
                "namespace": namespace,
                "gateway_class_name": "nginx",
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "investigate_gateway_connectivity",
        lambda namespace, gateway_name: {
            "success": True,
            "gateway": gateway_name,
            "problems": [
                {
                    "type": "GatewayNotProgrammed",
                    "severity": "critical",
                    "message": "Gateway is not programmed",
                }
            ],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": (
                "Why is my gateway not programmed?"
            ),
            "namespace": "default",
            "resource_name": "public-gateway",
        }
    )

    assert result["resource_type"] == "gateway"
    assert result["observations"]
    assert any(
        observation["tool"]
        == "investigate_gateway_connectivity"
        for observation in result["observations"]
    )
    assert result["recommendations"]
    assert result["verification_required"] is True


def test_scenario_http_route_backend_failure(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "list_httproutes",
        lambda namespace: {
            "success": True,
            "httproutes": [
                {
                    "name": "employment-route",
                    "namespace": namespace,
                    "rules": [],
                    "problems": [
                        {
                            "type": "NoBackendReferences",
                            "severity": "critical",
                        }
                    ],
                }
            ],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": (
                "Investigate my HTTPRoute "
                "employment-route"
            ),
            "namespace": "default",
            "resource_name": "employment-route",
        }
    )

    assert result["resource_type"] == "httproute"
    assert result["observations"]
    assert (
        result["observations"][0]["tool"]
        == "list_httproutes"
    )
    assert result["recommendations"]
    assert result["recommended_commands"]


def test_scenario_tool_failure_is_safe(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pod",
        lambda namespace, pod_name: {
            "success": False,
            "error": (
                "Kubernetes API error: "
                "Not Found"
            ),
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_logs",
        lambda namespace, pod_name: {
            "success": False,
            "error": (
                "Kubernetes API error: "
                "Not Found"
            ),
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_events",
        lambda namespace, pod_name: {
            "success": False,
            "error": (
                "Kubernetes API error: "
                "Not Found"
            ),
        },
    )

    result = nodes.read_infrastructure(
        {
            "user_request": "Inspect missing pod",
            "resource_type": "pod",
            "resource_name": "missing-pod",
            "namespace": "default",
        }
    )

    assert len(result["observations"]) == 3
    assert all(
        observation["status"] == "error"
        for observation in result["observations"]
    )
    assert all(
        "error" in observation
        for observation in result["observations"]
    )
