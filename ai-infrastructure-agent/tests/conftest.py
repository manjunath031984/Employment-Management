"""
Shared pytest fixtures for the AI Infrastructure Troubleshooting Agent.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Generic Fake Kubernetes Object
# ---------------------------------------------------------------------------


class FakeKubernetesObject(SimpleNamespace):
    """
    Lightweight fake Kubernetes API object.

    The production code uses Kubernetes model objects which provide
    a to_dict() method. SimpleNamespace does not provide that method,
    so this class emulates the required behavior for unit tests.
    """

    def to_dict(self):
        """Recursively convert the fake Kubernetes object to dictionaries."""

        def convert(value):
            if isinstance(value, SimpleNamespace):
                return {
                    key: convert(val)
                    for key, val in vars(value).items()
                }

            if isinstance(value, list):
                return [convert(item) for item in value]

            if isinstance(value, dict):
                return {
                    key: convert(val)
                    for key, val in value.items()
                }

            return value

        return convert(self)


# ---------------------------------------------------------------------------
# Kubernetes Object Helpers
# ---------------------------------------------------------------------------


def make_container_status(
    name: str = "app",
    ready: bool = True,
    restart_count: int = 0,
    state: str = "running",
):
    """
    Create a fake Kubernetes ContainerStatus object.
    """

    if state == "running":
        container_state = FakeKubernetesObject(
            running=FakeKubernetesObject(
                started_at=datetime.now(timezone.utc),
            ),
            waiting=None,
            terminated=None,
        )

    elif state == "waiting":
        container_state = FakeKubernetesObject(
            running=None,
            waiting=FakeKubernetesObject(
                reason="CrashLoopBackOff",
                message="Back-off restarting failed container",
            ),
            terminated=None,
        )

    elif state == "oom":
        container_state = FakeKubernetesObject(
            running=None,
            waiting=None,
            terminated=FakeKubernetesObject(
                reason="OOMKilled",
                exit_code=137,
                signal=None,
                message="Container exceeded memory limit",
                started_at=datetime.now(timezone.utc),
                finished_at=datetime.now(timezone.utc),
            ),
        )

    else:
        container_state = FakeKubernetesObject(
            running=None,
            waiting=None,
            terminated=FakeKubernetesObject(
                reason="Error",
                exit_code=1,
                signal=None,
                message="Application failed",
                started_at=datetime.now(timezone.utc),
                finished_at=datetime.now(timezone.utc),
            ),
        )

    return FakeKubernetesObject(
        name=name,
        ready=ready,
        restart_count=restart_count,
        started=ready,
        image="nginx:latest",
        image_id="docker://test-image",
        state=container_state,
        last_state=FakeKubernetesObject(
            running=None,
            waiting=None,
            terminated=None,
        ),
    )



def make_pod(
    name: str = "test-pod",
    namespace: str = "default",
    phase: str = "Running",
    ready: bool = True,
    restart_count: int = 0,
    labels: dict | None = None,
    container_state: str = "running",
):
    """
    Create a fake Kubernetes Pod.

    Uses FakeKubernetesObject so production code can call to_dict().
    """

    if labels is None:
        labels = {
            "app": "test-app",
        }

    readiness_condition = FakeKubernetesObject(
        type="Ready",
        status="True" if ready else "False",
        reason=None if ready else "ContainersNotReady",
        message=None if ready else "Container is not ready",
        last_transition_time=datetime.now(timezone.utc),
    )

    containers = [
        FakeKubernetesObject(
            name="app",
            image="nginx:latest",
            image_pull_policy="IfNotPresent",
            resources=FakeKubernetesObject(
                requests={
                    "cpu": "100m",
                    "memory": "128Mi",
                },
                limits={
                    "cpu": "500m",
                    "memory": "256Mi",
                },
            ),
            ports=[
                FakeKubernetesObject(
                    name="http",
                    container_port=8080,
                    protocol="TCP",
                )
            ],
            env=[
                FakeKubernetesObject(
                    name="APP_ENV",
                    value="test",
                ),
                FakeKubernetesObject(
                    name="DB_PASSWORD",
                    value="SECRET_VALUE",
                ),
            ],
        )
    ]

    return FakeKubernetesObject(
        metadata=SimpleNamespace(
            name=name,
            namespace=namespace,
            labels=labels,
            annotations={},
            generation=1,
        ),
        spec=FakeKubernetesObject(
            node_name="test-node",
            service_account_name="default",
            containers=containers,
        ),
        status=FakeKubernetesObject(
            phase=phase,
            pod_ip="10.0.0.10",
            host_ip="192.168.1.10",
            container_statuses=[
                make_container_status(
                    ready=ready,
                    restart_count=restart_count,
                    state=container_state,
                )
            ],
            conditions=[
                readiness_condition,
            ],
        ),
    )


def make_deployment(
    name: str = "test-deployment",
    namespace: str = "default",
    desired: int = 2,
    ready: int = 2,
    available: int = 2,
    updated: int = 2,
    unavailable: int = 0,
):
    """
    Create a fake Kubernetes Deployment.
    """

    return SimpleNamespace(
        metadata=SimpleNamespace(
            name=name,
            namespace=namespace,
            labels={
                "app": "test-app",
            },
            annotations={
                "deployment.kubernetes.io/revision": "1",
            },
            generation=1,
        ),
        spec=SimpleNamespace(
            replicas=desired,
            selector=SimpleNamespace(
                match_labels={
                    "app": "test-app",
                },
                match_expressions=[],
            ),
            strategy=SimpleNamespace(
                type="RollingUpdate",
                rolling_update=SimpleNamespace(
                    max_unavailable="25%",
                    max_surge="25%",
                ),
            ),
            min_ready_seconds=0,
            revision_history_limit=10,
            template=SimpleNamespace(
                spec=SimpleNamespace(
                    containers=[
                        SimpleNamespace(
                            name="app",
                            image="nginx:latest",
                            image_pull_policy="IfNotPresent",
                            resources=SimpleNamespace(
                                requests={
                                    "cpu": "100m",
                                    "memory": "128Mi",
                                },
                                limits={
                                    "cpu": "500m",
                                    "memory": "256Mi",
                                },
                            ),
                            ports=[
                                SimpleNamespace(
                                    name="http",
                                    container_port=8080,
                                    protocol="TCP",
                                )
                            ],
                            env=[
                                SimpleNamespace(
                                    name="APP_ENV",
                                    value="test",
                                )
                            ],
                        )
                    ]
                )
            ),
        ),
        status=SimpleNamespace(
            replicas=desired,
            ready_replicas=ready,
            available_replicas=available,
            updated_replicas=updated,
            unavailable_replicas=unavailable,
            observed_generation=1,
            conditions=[
                SimpleNamespace(
                    type="Available",
                    status="True" if available > 0 else "False",
                    reason="MinimumReplicasAvailable",
                    message="Deployment has minimum availability.",
                    last_update_time=datetime.now(timezone.utc),
                    last_transition_time=datetime.now(timezone.utc),
                ),
                SimpleNamespace(
                    type="Progressing",
                    status="True",
                    reason="NewReplicaSetAvailable",
                    message="ReplicaSet has successfully progressed.",
                    last_update_time=datetime.now(timezone.utc),
                    last_transition_time=datetime.now(timezone.utc),
                ),
            ],
        ),
    )


def make_service(
    name: str = "test-service",
    namespace: str = "default",
    selector: dict | None = None,
):
    """
    Create a fake Kubernetes Service.
    """

    if selector is None:
        selector = {
            "app": "test-app",
        }

    return SimpleNamespace(
        metadata=SimpleNamespace(
            name=name,
            namespace=namespace,
            labels={
                "app": "test-app",
            },
            annotations={},
        ),
        spec=SimpleNamespace(
            type="ClusterIP",
            cluster_ip="10.96.0.10",
            cluster_ips=["10.96.0.10"],
            external_ips=[],
            external_name=None,
            selector=selector,
            session_affinity="None",
            publish_not_ready_addresses=False,
            internal_traffic_policy="Cluster",
            external_traffic_policy="Cluster",
            ports=[
                SimpleNamespace(
                    name="http",
                    port=8080,
                    target_port=8080,
                    protocol="TCP",
                    node_port=None,
                    app_protocol=None,
                )
            ],
        ),
    )


def make_endpoints(
    ready: int = 1,
    not_ready: int = 0,
):
    """
    Create fake Kubernetes Endpoints.
    """

    ready_addresses = [
        SimpleNamespace(
            ip=f"10.0.0.{index + 10}",
            node_name="test-node",
            hostname=None,
            target_ref=SimpleNamespace(
                name=f"test-pod-{index}",
                kind="Pod",
            ),
        )
        for index in range(ready)
    ]

    not_ready_addresses = [
        SimpleNamespace(
            ip=f"10.0.1.{index + 10}",
            node_name="test-node",
            hostname=None,
            target_ref=SimpleNamespace(
                name=f"test-pod-not-ready-{index}",
                kind="Pod",
            ),
        )
        for index in range(not_ready)
    ]

    return SimpleNamespace(
        subsets=[
            SimpleNamespace(
                addresses=ready_addresses,
                not_ready_addresses=not_ready_addresses,
                ports=[
                    SimpleNamespace(
                        name="http",
                        port=8080,
                        protocol="TCP",
                    )
                ],
            )
        ]
        if ready or not_ready
        else []
    )


# ---------------------------------------------------------------------------
# Gateway API Objects
# ---------------------------------------------------------------------------


@pytest.fixture
def gateway_object():
    """
    Sample Gateway API object.
    """

    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {
            "name": "test-gateway",
            "namespace": "default",
            "labels": {
                "app": "gateway",
            },
            "annotations": {},
        },
        "spec": {
            "gatewayClassName": "test-gateway-class",
            "listeners": [
                {
                    "name": "http",
                    "hostname": "example.com",
                    "port": 80,
                    "protocol": "HTTP",
                    "allowedRoutes": {
                        "namespaces": {
                            "from": "Same"
                        }
                    },
                }
            ],
        },
        "status": {
            "addresses": [
                {
                    "type": "IPAddress",
                    "value": "10.0.0.100",
                }
            ],
            "conditions": [
                {
                    "type": "Accepted",
                    "status": "True",
                    "reason": "Accepted",
                    "message": "Gateway accepted.",
                },
                {
                    "type": "Programmed",
                    "status": "True",
                    "reason": "Programmed",
                    "message": "Gateway programmed.",
                },
            ],
            "listeners": [
                {
                    "name": "http",
                    "conditions": [
                        {
                            "type": "Accepted",
                            "status": "True",
                            "reason": "Accepted",
                            "message": "Listener accepted.",
                        }
                    ],
                }
            ],
        },
    }


@pytest.fixture
def httproute_object():
    """
    Sample HTTPRoute API object.
    """

    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {
            "name": "test-route",
            "namespace": "default",
            "labels": {},
            "annotations": {},
        },
        "spec": {
            "parentRefs": [
                {
                    "name": "test-gateway",
                }
            ],
            "hostnames": [
                "example.com"
            ],
            "rules": [
                {
                    "matches": [
                        {
                            "path": {
                                "type": "PathPrefix",
                                "value": "/",
                            }
                        }
                    ],
                    "backendRefs": [
                        {
                            "name": "test-service",
                            "port": 8080,
                            "weight": 1,
                        }
                    ],
                }
            ],
        },
        "status": {
            "parents": [
                {
                    "parentRef": {
                        "name": "test-gateway",
                    },
                    "conditions": [
                        {
                            "type": "Accepted",
                            "status": "True",
                            "reason": "Accepted",
                            "message": "Route accepted.",
                        },
                        {
                            "type": "ResolvedRefs",
                            "status": "True",
                            "reason": "ResolvedRefs",
                            "message": "References resolved.",
                        },
                    ],
                }
            ]
        },
    }


# ---------------------------------------------------------------------------
# Kubernetes Client Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_clients(monkeypatch):
    """
    Create mocked Kubernetes API clients and patch all tool modules.
    """

    mock_clients = {
        "core_v1": MagicMock(),
        "apps_v1": MagicMock(),
        "custom_objects": MagicMock(),
        "networking_v1": MagicMock(),
    }

    # Base client factory
    monkeypatch.setattr(
        "app.kubernetes.client.get_kubernetes_clients",
        lambda: mock_clients,
    )

    # Patch imported references used by individual tool modules.
    monkeypatch.setattr(
        "app.tools.kubernetes_tools.get_kubernetes_clients",
        lambda: mock_clients,
    )

    monkeypatch.setattr(
        "app.tools.pod_tools.get_kubernetes_clients",
        lambda: mock_clients,
    )

    monkeypatch.setattr(
        "app.tools.deployment_tools.get_kubernetes_clients",
        lambda: mock_clients,
    )

    monkeypatch.setattr(
        "app.tools.service_tools.get_kubernetes_clients",
        lambda: mock_clients,
    )

    monkeypatch.setattr(
        "app.tools.gateway_tools.get_kubernetes_clients",
        lambda: mock_clients,
    )

    return mock_clients