"""
Tests for Gateway API troubleshooting tools.
"""

from app.tools.gateway_tools import (
    detect_gateway_problems,
    detect_httproute_problems,
    get_gateway_conditions,
    get_gateway_listeners,
    get_httproute_backends,
    get_httproute_status,
    inspect_gateway,
    inspect_gatewayclass,
    inspect_httproute,
    investigate_gateway_connectivity,
    investigate_gateway_routes,
    list_gatewayclasses,
    list_gateways,
    list_httproutes,
)


def configure_gateway_mocks(
    mock_clients,
    gateway_object,
    httproute_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.side_effect = (
        lambda **kwargs:
        gateway_object
        if kwargs["plural"] == "gateways"
        else httproute_object
    )

    mock_clients[
        "custom_objects"
    ].get_cluster_custom_object.return_value = {
        "metadata": {
            "name": "test-gateway-class"
        },
        "spec": {
            "controllerName": (
                "example.com/controller"
            )
        },
        "status": {
            "conditions": [
                {
                    "type": "Accepted",
                    "status": "True",
                }
            ]
        },
    }


def test_list_gatewayclasses(
    mock_clients,
):

    mock_clients[
        "custom_objects"
    ].list_cluster_custom_object.return_value = {
        "items": [
            {
                "metadata": {
                    "name": "test-gateway-class"
                },
                "spec": {
                    "controllerName": (
                        "example.com/controller"
                    )
                },
                "status": {
                    "conditions": []
                },
            }
        ]
    }

    result = list_gatewayclasses()

    assert result["success"] is True

    assert result["count"] == 1


def test_inspect_gatewayclass(
    mock_clients,
):

    mock_clients[
        "custom_objects"
    ].get_cluster_custom_object.return_value = {
        "metadata": {
            "name": "test-gateway-class",
            "labels": {},
            "annotations": {},
        },
        "spec": {
            "controllerName": (
                "example.com/controller"
            )
        },
        "status": {
            "conditions": []
        },
    }

    result = inspect_gatewayclass(
        "test-gateway-class"
    )

    assert result["success"] is True

    assert (
        result["gatewayclass"]["name"]
        == "test-gateway-class"
    )


def test_list_gateways(
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

    result = list_gateways(
        "default"
    )

    assert result["success"] is True

    assert result["count"] == 1


def test_inspect_gateway(
    mock_clients,
    gateway_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        gateway_object
    )

    result = inspect_gateway(
        "default",
        "test-gateway",
    )

    assert result["success"] is True

    assert (
        result["gateway"]["name"]
        == "test-gateway"
    )


def test_gateway_listeners(
    mock_clients,
    gateway_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        gateway_object
    )

    result = get_gateway_listeners(
        "default",
        "test-gateway",
    )

    assert result["success"] is True

    assert result["listener_count"] == 1

    assert (
        result["listeners"][0]["port"]
        == 80
    )


def test_gateway_conditions(
    mock_clients,
    gateway_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        gateway_object
    )

    result = get_gateway_conditions(
        "default",
        "test-gateway",
    )

    assert result["success"] is True

    assert result["conditions"]


def test_detect_gateway_problems_healthy(
    mock_clients,
    gateway_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        gateway_object
    )

    result = detect_gateway_problems(
        "default",
        "test-gateway",
    )

    assert result["success"] is True

    assert result["problem_count"] == 0


def test_detect_gateway_not_programmed(
    mock_clients,
    gateway_object,
):

    broken_gateway = dict(
        gateway_object
    )

    broken_gateway["status"] = {
        "conditions": [
            {
                "type": "Accepted",
                "status": "True",
            },
            {
                "type": "Programmed",
                "status": "False",
                "reason": "ProgrammedError",
                "message": "Gateway not programmed.",
            },
        ],
        "listeners": [],
        "addresses": [],
    }

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        broken_gateway
    )

    result = detect_gateway_problems(
        "default",
        "test-gateway",
    )

    problem_types = [
        problem["type"]
        for problem in result["problems"]
    ]

    assert (
        "GatewayNotProgrammed"
        in problem_types
    )


def test_list_httproutes(
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

    result = list_httproutes(
        "default"
    )

    assert result["success"] is True

    assert result["count"] == 1


def test_inspect_httproute(
    mock_clients,
    httproute_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        httproute_object
    )

    result = inspect_httproute(
        "default",
        "test-route",
    )

    assert result["success"] is True

    assert (
        result["httproute"]["name"]
        == "test-route"
    )


def test_httproute_status(
    mock_clients,
    httproute_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        httproute_object
    )

    result = get_httproute_status(
        "default",
        "test-route",
    )

    assert result["success"] is True

    assert result["parent_status"]


def test_httproute_backends(
    mock_clients,
    httproute_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        httproute_object
    )

    result = get_httproute_backends(
        "default",
        "test-route",
    )

    assert result["success"] is True

    assert result["backend_count"] == 1

    assert (
        result["backends"][0]["name"]
        == "test-service"
    )


def test_httproute_problems_healthy(
    mock_clients,
    httproute_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        httproute_object
    )

    result = detect_httproute_problems(
        "default",
        "test-route",
    )

    assert result["success"] is True

    assert result["problem_count"] == 0


def test_httproute_missing_backend(
    mock_clients,
    httproute_object,
):

    broken_route = dict(
        httproute_object
    )

    broken_route["spec"] = {
        "parentRefs": [
            {
                "name": "test-gateway"
            }
        ],
        "rules": [
            {}
        ],
    }

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        broken_route
    )

    result = detect_httproute_problems(
        "default",
        "test-route",
    )

    problem_types = [
        problem["type"]
        for problem in result["problems"]
    ]

    assert (
        "NoBackendReferences"
        in problem_types
    )


def test_gateway_routes(
    mock_clients,
    gateway_object,
    httproute_object,
):

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.return_value = (
        gateway_object
    )

    mock_clients[
        "custom_objects"
    ].list_namespaced_custom_object.return_value = {
        "items": [
            httproute_object
        ]
    }

    result = investigate_gateway_routes(
        "default",
        "test-gateway",
    )

    assert result["success"] is True

    assert (
        result["attached_route_count"]
        == 1
    )


def test_full_gateway_investigation(
    mock_clients,
    gateway_object,
    httproute_object,
):

    # Gateway and HTTPRoute lookups

    def get_object(**kwargs):

        if kwargs["plural"] == "gateways":

            return gateway_object

        return httproute_object

    mock_clients[
        "custom_objects"
    ].get_namespaced_custom_object.side_effect = (
        get_object
    )

    mock_clients[
        "custom_objects"
    ].get_cluster_custom_object.return_value = {
        "metadata": {
            "name": "test-gateway-class"
        },
        "spec": {
            "controllerName": (
                "example.com/controller"
            )
        },
        "status": {
            "conditions": []
        },
    }

    mock_clients[
        "custom_objects"
    ].list_namespaced_custom_object.return_value = {
        "items": [
            httproute_object
        ]
    }

    result = investigate_gateway_connectivity(
        "default",
        "test-gateway",
    )

    assert result["success"] is True, result

    assert "gatewayclass" in result

    assert "gateway" in result

    assert "listeners" in result

    assert "routes" in result