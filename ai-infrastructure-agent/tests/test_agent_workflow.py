"""
End-to-end LangGraph workflow tests using mocked Kubernetes evidence.

No Kubernetes cluster is required.
"""

from app.agent.graph import infra_graph
from app.agent import nodes


def test_full_crashloop_workflow_with_mocked_kubernetes(monkeypatch):
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
                        "name": "employment-management",
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
            "logs": (
                "ERROR Database connection refused "
                "to postgres:5432"
            ),
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
                    "message": (
                        "Back-off restarting failed container"
                    ),
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

    assert result["observations"]
    assert result["pods"]
    assert result["logs"]
    assert result["events"]

    assert result["root_cause"]
    assert result["confidence"] == 0.65

    assert result["recommendations"]
    assert result["recommended_commands"]
    assert result["verification_required"] is True
    assert result["final_response"]


def test_full_generic_workflow_with_mocked_kubernetes(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "get_pods",
        lambda namespace=None: {
            "success": True,
            "pods": [
                {
                    "name": "employment-management-abc",
                    "namespace": namespace or "default",
                    "phase": "Running",
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
                    "name": "employment-management",
                    "namespace": namespace or "default",
                    "ready_replicas": 2,
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
                    "name": "employment-management",
                    "namespace": namespace or "default",
                    "type": "ClusterIP",
                }
            ],
        },
    )

    result = infra_graph.invoke(
        {
            "user_request": (
                "Investigate the health of my "
                "Kubernetes application"
            ),
            "namespace": "employment-management",
        }
    )

    assert result["observations"]
    assert result["pods"]
    assert result["deployments"]
    assert result["services"]

    assert result["diagnosis"]
    assert result["recommendations"]
    assert result["recommended_commands"]
    assert result["verification_required"] is True
