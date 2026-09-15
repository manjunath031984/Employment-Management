"""
Tests for generic Kubernetes tools.
"""

from app.tools.kubernetes_tools import (
    get_deployment,
    get_deployments,
    get_endpoints,
    get_gateways,
    get_httproutes,
    get_namespace,
    get_namespaces,
    get_pod,
    get_pod_events,
    get_pod_logs,
    get_pods,
    get_pvcs,
    get_service,
    get_services,
    get_statefulsets,
)


def test_get_namespaces(mock_clients):

    mock_clients[
        "core_v1"
    ].list_namespace.return_value = type(
        "Response",
        (),
        {
            "items": [
                type(
                    "Namespace",
                    (),
                    {
                        "metadata": type(
                            "Metadata",
                            (),
                            {"name": "default"},
                        )(),
                        "status": type(
                            "Status",
                            (),
                            {"phase": "Active"},
                        )(),
                    },
                )()
            ]
        },
    )()

    result = get_namespaces()

    assert result["success"] is True

    assert result["count"] == 1

    assert (
        result["namespaces"][0]["name"]
        == "default"
    )


def test_get_namespace(mock_clients):

    namespace = type(
        "Namespace",
        (),
        {
            "metadata": type(
                "Metadata",
                (),
                {
                    "name": "default",
                    "labels": {},
                    "annotations": {},
                },
            )(),
            "status": type(
                "Status",
                (),
                {"phase": "Active"},
            )(),
        },
    )()

    mock_clients[
        "core_v1"
    ].read_namespace.return_value = namespace

    result = get_namespace("default")

    assert result["success"] is True

    assert (
        result["namespace"]["name"]
        == "default"
    )


def test_get_pods(mock_clients):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].list_namespaced_pod.return_value = type(
        "Response",
        (),
        {
            "items": [
                make_pod()
            ]
        },
    )()

    result = get_pods("default")

    assert result["success"] is True

    assert result["count"] == 1

    assert (
        result["pods"][0]["name"]
        == "test-pod"
    )


def test_get_pod(mock_clients):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = (
        make_pod()
    )

    result = get_pod(
        "default",
        "test-pod",
    )

    assert result["success"] is True, result

    assert (
        result["pod"]["name"]
        == "test-pod"
    )


def test_get_pod_logs(mock_clients):

    mock_clients[
        "core_v1"
    ].read_namespaced_pod_log.return_value = (
        "application started"
    )

    result = get_pod_logs(
        "default",
        "test-pod",
    )

    assert result["success"] is True

    assert (
        result["logs"]
        == "application started"
    )


def test_get_pod_events(mock_clients):

    from tests.conftest import make_pod

    event = type(
        "Event",
        (),
        {
            "type": "Warning",
            "reason": "BackOff",
            "message": "Container restarting",
            "count": 3,
            "first_timestamp": None,
            "last_timestamp": None,
            "involved_object": type(
                "Object",
                (),
                {
                    "kind": "Pod",
                    "name": "test-pod",
                },
            )(),
        },
    )()

    mock_clients[
        "core_v1"
    ].list_namespaced_event.return_value = type(
        "Response",
        (),
        {
            "items": [event]
        },
    )()

    result = get_pod_events(
        "default",
        "test-pod",
    )

    assert result["success"] is True

    assert result["count"] == 1

    assert (
        result["events"][0]["reason"]
        == "BackOff"
    )


def test_get_deployments(mock_clients):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].list_namespaced_deployment.return_value = type(
        "Response",
        (),
        {
            "items": [
                make_deployment()
            ]
        },
    )()

    result = get_deployments("default")

    assert result["success"] is True

    assert result["count"] == 1


def test_get_deployment(mock_clients):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment()
    )

    result = get_deployment(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert (
        result["deployment"]["name"]
        == "test-deployment"
    )


def test_get_services(mock_clients):

    from tests.conftest import make_service

    mock_clients[
        "core_v1"
    ].list_namespaced_service.return_value = type(
        "Response",
        (),
        {
            "items": [
                make_service()
            ]
        },
    )()

    result = get_services("default")

    assert result["success"] is True

    assert result["count"] == 1


def test_get_service(mock_clients):

    from tests.conftest import make_service

    mock_clients[
        "core_v1"
    ].read_namespaced_service.return_value = (
        make_service()
    )

    result = get_service(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert (
        result["service"]["name"]
        == "test-service"
    )


def test_get_endpoints(mock_clients):

    from tests.conftest import make_endpoints

    mock_clients[
        "core_v1"
    ].read_namespaced_endpoints.return_value = (
        make_endpoints(
            ready=2,
            not_ready=1,
        )
    )

    result = get_endpoints(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert (
        result["subsets"]
    )


def test_get_statefulsets(mock_clients):

    statefulset = type(
        "StatefulSet",
        (),
        {
            "metadata": type(
                "Metadata",
                (),
                {
                    "name": "postgres",
                    "namespace": "default",
                },
            )(),
            "spec": type(
                "Spec",
                (),
                {"replicas": 1},
            )(),
            "status": type(
                "Status",
                (),
                {
                    "ready_replicas": 1,
                    "current_replicas": 1,
                },
            )(),
        },
    )()

    mock_clients[
        "apps_v1"
    ].list_namespaced_stateful_set.return_value = type(
        "Response",
        (),
        {
            "items": [
                statefulset
            ]
        },
    )()

    result = get_statefulsets("default")

    assert result["success"] is True

    assert result["count"] == 1


def test_get_pvcs(mock_clients):

    pvc = type(
        "PVC",
        (),
        {
            "metadata": type(
                "Metadata",
                (),
                {
                    "name": "postgres-pvc",
                    "namespace": "default",
                },
            )(),
            "status": type(
                "Status",
                (),
                {"phase": "Bound"},
            )(),
            "spec": type(
                "Spec",
                (),
                {
                    "storage_class_name": "standard",
                    "resources": type(
                        "Resources",
                        (),
                        {
                            "requests": {
                                "storage": "10Gi"
                            }
                        },
                    )(),
                    "volume_name": "pv-test",
                },
            )(),
        },
    )()

    mock_clients[
        "core_v1"
    ].list_namespaced_persistent_volume_claim.return_value = type(
        "Response",
        (),
        {
            "items": [
                pvc
            ]
        },
    )()

    result = get_pvcs("default")

    assert result["success"] is True

    assert result["count"] == 1


def test_get_gateways(
    mock_clients,
    gateway_object,
):

    mock_clients[
        "custom_objects"
    ].list_namespaced_custom_object.return_value = {
        "items": [
            gateway_object
        ]
    }

    result = get_gateways("default")

    assert result["success"] is True

    assert result["count"] == 1


def test_get_httproutes(
    mock_clients,
    httproute_object,
):

    mock_clients[
        "custom_objects"
    ].list_namespaced_custom_object.return_value = {
        "items": [
            httproute_object
        ]
    }

    result = get_httproutes("default")

    assert result["success"] is True

    assert result["count"] == 1