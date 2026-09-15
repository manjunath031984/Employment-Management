"""
Integration tests for the LangGraph read-infrastructure node.

These tests use mocked read-only Kubernetes tools, so no Kubernetes
cluster is required.
"""

from app.agent import nodes


def test_read_infrastructure_pod_collects_evidence(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pod",
        lambda namespace, pod_name: {
            "success": True,
            "pod": {
                "name": pod_name,
                "namespace": namespace,
                "phase": "Running",
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_logs",
        lambda namespace, pod_name: {
            "success": True,
            "logs": "application started successfully",
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_pod_events",
        lambda namespace, pod_name: {
            "success": True,
            "events": [
                {
                    "type": "Normal",
                    "reason": "Started",
                }
            ],
        },
    )

    result = nodes.read_infrastructure(
        {
            "user_request": "Inspect my pod demo-pod",
            "resource_type": "pod",
            "resource_name": "demo-pod",
            "namespace": "default",
        }
    )

    assert len(result["pods"]) == 1
    assert result["pods"][0]["name"] == "demo-pod"
    assert result["logs"] == [
        "application started successfully"
    ]
    assert result["events"][0]["reason"] == "Started"

    tools = [
        observation["tool"]
        for observation in result["observations"]
    ]

    assert tools == [
        "get_pod",
        "get_pod_logs",
        "get_pod_events",
    ]


def test_read_infrastructure_service_collects_endpoints(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_service",
        lambda namespace, service_name: {
            "success": True,
            "service": {
                "name": service_name,
                "namespace": namespace,
                "type": "ClusterIP",
            },
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_endpoints",
        lambda namespace, service_name: {
            "success": True,
            "ready_endpoint_count": 2,
            "not_ready_endpoint_count": 0,
            "ready_endpoints": [
                {"ip": "10.0.0.10"},
                {"ip": "10.0.0.11"},
            ],
        },
    )

    result = nodes.read_infrastructure(
        {
            "user_request": "Inspect service demo-service",
            "resource_type": "service",
            "resource_name": "demo-service",
            "namespace": "default",
        }
    )

    assert len(result["services"]) == 1
    assert (
        result["services"][0]["name"]
        == "demo-service"
    )

    assert len(result["observations"]) == 2
    assert (
        result["observations"][1]["tool"]
        == "get_endpoints"
    )
    assert (
        result["observations"][1]["status"]
        == "success"
    )


def test_read_infrastructure_generic_overview(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pods",
        lambda namespace=None: {
            "success": True,
            "pods": [
                {
                    "name": "demo-pod",
                    "namespace": namespace or "default",
                }
            ],
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_deployments",
        lambda namespace=None: {
            "success": True,
            "deployments": [
                {
                    "name": "demo-deployment",
                    "namespace": namespace or "default",
                }
            ],
        },
    )
    monkeypatch.setattr(
        nodes,
        "get_services",
        lambda namespace=None: {
            "success": True,
            "services": [
                {
                    "name": "demo-service",
                    "namespace": namespace or "default",
                }
            ],
        },
    )

    result = nodes.read_infrastructure(
        {
            "user_request": "Why is my application unhealthy?",
            "resource_type": None,
            "resource_name": None,
            "namespace": "default",
        }
    )

    assert len(result["pods"]) == 1
    assert len(result["deployments"]) == 1
    assert len(result["services"]) == 1

    assert [
        observation["tool"]
        for observation in result["observations"]
    ] == [
        "get_pods",
        "get_deployments",
        "get_services",
    ]


def test_read_infrastructure_tool_error_is_structured(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_deployment",
        lambda namespace, deployment_name: {
            "success": False,
            "error": "Kubernetes API error: Not Found",
        },
    )

    result = nodes.read_infrastructure(
        {
            "user_request": "Inspect deployment missing-deployment",
            "resource_type": "deployment",
            "resource_name": "missing-deployment",
            "namespace": "default",
        }
    )

    assert len(result["observations"]) == 1

    observation = result["observations"][0]

    assert observation["tool"] == "get_deployment"
    assert observation["status"] == "error"
    assert (
        observation["error"]
        == "Kubernetes API error: Not Found"
    )

    assert result["error"] is None
