"""
Tests for Service troubleshooting tools.
"""

from app.tools.service_tools import (
    detect_service_problems,
    get_service_endpoints,
    inspect_service,
    inspect_service_selector,
    investigate_service_connectivity,
    list_services,
    validate_service_ports,
)


def test_inspect_service(
    mock_clients,
):

    from tests.conftest import make_service

    mock_clients[
        "core_v1"
    ].read_namespaced_service.return_value = (
        make_service()
    )

    result = inspect_service(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert (
        result["service"]["name"]
        == "test-service"
    )

    assert (
        result["service"]["cluster_ip"]
        == "10.96.0.10"
    )


def test_list_services(
    mock_clients,
):

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

    result = list_services(
        "default"
    )

    assert result["success"] is True

    assert result["count"] == 1


def test_get_service_endpoints(
    mock_clients,
):

    from tests.conftest import make_endpoints

    mock_clients[
        "core_v1"
    ].read_namespaced_endpoints.return_value = (
        make_endpoints(
            ready=2,
            not_ready=1,
        )
    )

    result = get_service_endpoints(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert (
        result["ready_endpoint_count"]
        == 2
    )

    assert (
        result["not_ready_endpoint_count"]
        == 1
    )

    assert (
        result["has_ready_endpoints"]
        is True
    )




def test_detect_no_endpoints(
    mock_clients,
):

    from tests.conftest import (
        make_endpoints,
        make_service,
    )

    mock_clients[
        "core_v1"
    ].read_namespaced_service.return_value = (
        make_service()
    )

    mock_clients[
        "core_v1"
    ].read_namespaced_endpoints.return_value = (
        make_endpoints(
            ready=0,
            not_ready=0,
        )
    )

    result = detect_service_problems(
        "default",
        "test-service",
    )

    problem_types = [
        problem["type"]
        for problem in result["problems"]
    ]

    assert (
        "NoEndpoints"
        in problem_types
    )


def test_service_selector(
    mock_clients,
):

    from tests.conftest import make_pod
    from tests.conftest import make_service

    mock_clients[
        "core_v1"
    ].read_namespaced_service.return_value = (
        make_service()
    )

    mock_clients[
        "core_v1"
    ].list_namespaced_pod.return_value = type(
        "Response",
        (),
        {
            "items": [
                make_pod(),
                make_pod(
                    name="test-pod-2"
                ),
            ]
        },
    )()

    result = inspect_service_selector(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert (
        result["matching_pod_count"]
        == 2
    )

    assert (
        result["ready_pod_count"]
        == 2
    )


def test_service_selector_no_selector(
    mock_clients,
):

    from tests.conftest import make_service

    service = make_service(
        selector={}
    )

    mock_clients[
        "core_v1"
    ].read_namespaced_service.return_value = (
        service
    )

    result = inspect_service_selector(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert (
        result["matching_pod_count"]
        == 0
    )


def test_validate_service_ports(
    mock_clients,
):

    from tests.conftest import (
        make_pod,
        make_service,
    )

    mock_clients[
        "core_v1"
    ].read_namespaced_service.return_value = (
        make_service()
    )

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

    result = validate_service_ports(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert result["valid"] is True

    assert result["ports"]


def test_full_service_investigation(
    mock_clients,
):

    from tests.conftest import (
        make_endpoints,
        make_pod,
        make_service,
    )

    mock_clients[
        "core_v1"
    ].read_namespaced_service.return_value = (
        make_service()
    )

    mock_clients[
        "core_v1"
    ].read_namespaced_endpoints.return_value = (
        make_endpoints(
            ready=1
        )
    )

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

    result = investigate_service_connectivity(
        "default",
        "test-service",
    )

    assert result["success"] is True

    assert (
        result["service"]
        == "test-service"
    )

    assert (
        "endpoint_analysis"
        in result
    )

    assert (
        "selector_analysis"
        in result
    )

    assert (
        "problem_analysis"
        in result
    )