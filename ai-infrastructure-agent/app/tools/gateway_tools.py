"""
Gateway API troubleshooting tools for the AI Infrastructure Troubleshooting Agent.

Responsibilities:
- Inspect GatewayClass resources
- Inspect Gateway resources
- Inspect HTTPRoute resources
- Inspect Gateway listeners
- Inspect Gateway conditions
- Inspect HTTPRoute parent status
- Inspect HTTPRoute backend references
- Detect common Gateway API problems
- Investigate Gateway -> HTTPRoute -> Service relationships

IMPORTANT:
This module is READ-ONLY.

It does NOT:
- create Gateway resources
- update Gateway resources
- delete Gateway resources
- modify GatewayClass
- modify HTTPRoute
- modify Services
"""

from __future__ import annotations

from typing import Any

from kubernetes.client import ApiException

from app.kubernetes.client import get_kubernetes_clients


GATEWAY_API_GROUP = "gateway.networking.k8s.io"
GATEWAY_API_VERSION = "v1"


# ---------------------------------------------------------------------------
# GatewayClass
# ---------------------------------------------------------------------------


def list_gatewayclasses() -> dict[str, Any]:
    """
    List GatewayClass resources.

    GatewayClass is cluster-scoped.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        response = custom_objects.list_cluster_custom_object(
            group=GATEWAY_API_GROUP,
            version=GATEWAY_API_VERSION,
            plural="gatewayclasses",
        )

        gatewayclasses = []

        for item in response.get("items", []):

            metadata = item.get("metadata", {})
            spec = item.get("spec", {})
            status = item.get("status", {})

            gatewayclasses.append(
                {
                    "name": metadata.get("name"),
                    "controller_name": spec.get(
                        "controllerName"
                    ),
                    "description": spec.get(
                        "description"
                    ),
                    "parameters_ref": spec.get(
                        "parametersRef"
                    ),
                    "conditions": status.get(
                        "conditions",
                        [],
                    ),
                }
            )

        return {
            "success": True,
            "count": len(gatewayclasses),
            "gatewayclasses": gatewayclasses,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def inspect_gatewayclass(
    gatewayclass_name: str,
) -> dict[str, Any]:
    """
    Inspect a specific GatewayClass.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        gatewayclass = custom_objects.get_cluster_custom_object(
            group=GATEWAY_API_GROUP,
            version=GATEWAY_API_VERSION,
            plural="gatewayclasses",
            name=gatewayclass_name,
        )

        metadata = gatewayclass.get(
            "metadata",
            {},
        )

        spec = gatewayclass.get(
            "spec",
            {},
        )

        status = gatewayclass.get(
            "status",
            {},
        )

        return {
            "success": True,
            "gatewayclass": {
                "name": metadata.get("name"),
                "controller_name": spec.get(
                    "controllerName"
                ),
                "description": spec.get(
                    "description"
                ),
                "parameters_ref": spec.get(
                    "parametersRef"
                ),
                "conditions": status.get(
                    "conditions",
                    [],
                ),
                "labels": metadata.get(
                    "labels",
                    {},
                ),
                "annotations": metadata.get(
                    "annotations",
                    {},
                ),
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Gateway
# ---------------------------------------------------------------------------


def list_gateways(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    List Gateway resources.

    If namespace is None, Gateways from all namespaces are returned.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        if namespace:

            response = (
                custom_objects
                .list_namespaced_custom_object(
                    group=GATEWAY_API_GROUP,
                    version=GATEWAY_API_VERSION,
                    namespace=namespace,
                    plural="gateways",
                )
            )

        else:

            response = (
                custom_objects
                .list_cluster_custom_object(
                    group=GATEWAY_API_GROUP,
                    version=GATEWAY_API_VERSION,
                    plural="gateways",
                )
            )

        gateways = []

        for item in response.get("items", []):

            gateways.append(
                _serialize_gateway(item)
            )

        return {
            "success": True,
            "count": len(gateways),
            "gateways": gateways,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def inspect_gateway(
    namespace: str,
    gateway_name: str,
) -> dict[str, Any]:
    """
    Inspect a specific Gateway.

    Collects:
    - GatewayClass
    - addresses
    - listeners
    - conditions
    - attached routes
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        gateway = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="gateways",
                name=gateway_name,
            )
        )

        return {
            "success": True,
            "gateway": _serialize_gateway(
                gateway
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Gateway Listeners
# ---------------------------------------------------------------------------


def get_gateway_listeners(
    namespace: str,
    gateway_name: str,
) -> dict[str, Any]:
    """
    Inspect Gateway listeners.

    Useful for diagnosing:
    - incorrect listener port
    - unsupported protocol
    - hostname mismatch
    - listener not accepted
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        gateway = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="gateways",
                name=gateway_name,
            )
        )

        spec = gateway.get(
            "spec",
            {},
        )

        status = gateway.get(
            "status",
            {},
        )

        spec_listeners = spec.get(
            "listeners",
            [],
        )

        status_listeners = status.get(
            "listeners",
            [],
        )

        listeners = []

        for listener in spec_listeners:

            name = listener.get("name")

            status_listener = next(
                (
                    item
                    for item in status_listeners
                    if item.get("name") == name
                ),
                {},
            )

            listeners.append(
                {
                    "name": name,
                    "hostname": listener.get(
                        "hostname"
                    ),
                    "port": listener.get(
                        "port"
                    ),
                    "protocol": listener.get(
                        "protocol"
                    ),
                    "tls": listener.get(
                        "tls"
                    ),
                    "allowed_routes": listener.get(
                        "allowedRoutes"
                    ),
                    "status": status_listener,
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "gateway": gateway_name,
            "listener_count": len(listeners),
            "listeners": listeners,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Gateway Conditions
# ---------------------------------------------------------------------------


def get_gateway_conditions(
    namespace: str,
    gateway_name: str,
) -> dict[str, Any]:
    """
    Get Gateway status conditions.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        gateway = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="gateways",
                name=gateway_name,
            )
        )

        status = gateway.get(
            "status",
            {},
        )

        return {
            "success": True,
            "namespace": namespace,
            "gateway": gateway_name,
            "addresses": status.get(
                "addresses",
                [],
            ),
            "conditions": status.get(
                "conditions",
                [],
            ),
            "listeners": status.get(
                "listeners",
                [],
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# HTTPRoute
# ---------------------------------------------------------------------------


def list_httproutes(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    List HTTPRoute resources.

    If namespace is None, HTTPRoutes from all namespaces are returned.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        if namespace:

            response = (
                custom_objects
                .list_namespaced_custom_object(
                    group=GATEWAY_API_GROUP,
                    version=GATEWAY_API_VERSION,
                    namespace=namespace,
                    plural="httproutes",
                )
            )

        else:

            response = (
                custom_objects
                .list_cluster_custom_object(
                    group=GATEWAY_API_GROUP,
                    version=GATEWAY_API_VERSION,
                    plural="httproutes",
                )
            )

        routes = []

        for item in response.get("items", []):

            routes.append(
                _serialize_httproute(item)
            )

        return {
            "success": True,
            "count": len(routes),
            "httproutes": routes,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def inspect_httproute(
    namespace: str,
    httproute_name: str,
) -> dict[str, Any]:
    """
    Inspect a specific HTTPRoute.

    Collects:
    - hostnames
    - parentRefs
    - rules
    - backendRefs
    - route status
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        route = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="httproutes",
                name=httproute_name,
            )
        )

        return {
            "success": True,
            "httproute": _serialize_httproute(
                route
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# HTTPRoute Parent Status
# ---------------------------------------------------------------------------


def get_httproute_status(
    namespace: str,
    httproute_name: str,
) -> dict[str, Any]:
    """
    Inspect HTTPRoute parent status.

    Useful for determining whether a Gateway has accepted
    and programmed the HTTPRoute.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        route = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="httproutes",
                name=httproute_name,
            )
        )

        status = route.get(
            "status",
            {},
        )

        parents = status.get(
            "parents",
            [],
        )

        return {
            "success": True,
            "namespace": namespace,
            "httproute": httproute_name,
            "parent_status": parents,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# HTTPRoute Backend References
# ---------------------------------------------------------------------------


def get_httproute_backends(
    namespace: str,
    httproute_name: str,
) -> dict[str, Any]:
    """
    Extract backend Service references from an HTTPRoute.

    This is useful for connecting:

        HTTPRoute
             ↓
        backend Service
             ↓
        Endpoints
             ↓
        Pods
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        route = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="httproutes",
                name=httproute_name,
            )
        )

        spec = route.get(
            "spec",
            {},
        )

        backends = []

        for rule in spec.get(
            "rules",
            [],
        ):

            for backend in rule.get(
                "backendRefs",
                [],
            ):

                backends.append(
                    {
                        "name": backend.get(
                            "name"
                        ),
                        "namespace": backend.get(
                            "namespace",
                            namespace,
                        ),
                        "port": backend.get(
                            "port"
                        ),
                        "weight": backend.get(
                            "weight"
                        ),
                        "kind": backend.get(
                            "kind",
                            "Service",
                        ),
                        "group": backend.get(
                            "group",
                            "",
                        ),
                    }
                )

        return {
            "success": True,
            "namespace": namespace,
            "httproute": httproute_name,
            "backend_count": len(backends),
            "backends": backends,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Gateway Problems
# ---------------------------------------------------------------------------


def detect_gateway_problems(
    namespace: str,
    gateway_name: str,
) -> dict[str, Any]:
    """
    Detect common Gateway API problems.

    This function identifies diagnostic signals.

    It does NOT determine the final root cause.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        gateway = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="gateways",
                name=gateway_name,
            )
        )

        problems: list[dict[str, Any]] = []

        spec = gateway.get(
            "spec",
            {},
        )

        status = gateway.get(
            "status",
            {},
        )

        # ---------------------------------------------------------------
        # GatewayClass
        # ---------------------------------------------------------------

        gateway_class_name = spec.get(
            "gatewayClassName"
        )

        if not gateway_class_name:

            problems.append(
                {
                    "type": "MissingGatewayClass",
                    "severity": "critical",
                    "message": (
                        "Gateway does not specify a GatewayClass."
                    ),
                }
            )

        # ---------------------------------------------------------------
        # Gateway conditions
        # ---------------------------------------------------------------

        conditions = status.get(
            "conditions",
            [],
        )

        if not conditions:

            problems.append(
                {
                    "type": "MissingGatewayStatus",
                    "severity": "warning",
                    "message": (
                        "Gateway does not currently expose "
                        "status conditions."
                    ),
                }
            )

        for condition in conditions:

            condition_type = condition.get(
                "type"
            )

            condition_status = condition.get(
                "status"
            )

            if (
                condition_type == "Accepted"
                and condition_status != "True"
            ):

                problems.append(
                    {
                        "type": "GatewayNotAccepted",
                        "severity": "critical",
                        "reason": condition.get(
                            "reason"
                        ),
                        "message": condition.get(
                            "message"
                        ),
                    }
                )

            if (
                condition_type == "Programmed"
                and condition_status != "True"
            ):

                problems.append(
                    {
                        "type": "GatewayNotProgrammed",
                        "severity": "critical",
                        "reason": condition.get(
                            "reason"
                        ),
                        "message": condition.get(
                            "message"
                        ),
                    }
                )

        # ---------------------------------------------------------------
        # Listeners
        # ---------------------------------------------------------------

        listeners = spec.get(
            "listeners",
            [],
        )

        if not listeners:

            problems.append(
                {
                    "type": "NoGatewayListeners",
                    "severity": "critical",
                    "message": (
                        "Gateway does not define any listeners."
                    ),
                }
            )

        status_listeners = status.get(
            "listeners",
            [],
        )

        for listener in status_listeners:

            listener_name = listener.get(
                "name"
            )

            for condition in listener.get(
                "conditions",
                [],
            ):

                if (
                    condition.get("type")
                    == "Accepted"
                    and condition.get("status")
                    != "True"
                ):

                    problems.append(
                        {
                            "type": "ListenerNotAccepted",
                            "severity": "critical",
                            "listener": listener_name,
                            "reason": condition.get(
                                "reason"
                            ),
                            "message": condition.get(
                                "message"
                            ),
                        }
                    )

        # ---------------------------------------------------------------
        # Gateway addresses
        # ---------------------------------------------------------------

        addresses = status.get(
            "addresses",
            [],
        )

        if not addresses:

            problems.append(
                {
                    "type": "NoGatewayAddress",
                    "severity": "warning",
                    "message": (
                        "Gateway does not currently expose "
                        "a programmed address."
                    ),
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "gateway": gateway_name,
            "problem_count": len(problems),
            "problems": problems,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# HTTPRoute Problems
# ---------------------------------------------------------------------------


def detect_httproute_problems(
    namespace: str,
    httproute_name: str,
) -> dict[str, Any]:
    """
    Detect common HTTPRoute problems.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        route = (
            custom_objects
            .get_namespaced_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                namespace=namespace,
                plural="httproutes",
                name=httproute_name,
            )
        )

        problems: list[dict[str, Any]] = []

        spec = route.get(
            "spec",
            {},
        )

        status = route.get(
            "status",
            {},
        )

        # ---------------------------------------------------------------
        # Parent references
        # ---------------------------------------------------------------

        parent_refs = spec.get(
            "parentRefs",
            [],
        )

        if not parent_refs:

            problems.append(
                {
                    "type": "MissingParentGateway",
                    "severity": "critical",
                    "message": (
                        "HTTPRoute does not specify a parent Gateway."
                    ),
                }
            )

        # ---------------------------------------------------------------
        # Rules
        # ---------------------------------------------------------------

        rules = spec.get(
            "rules",
            [],
        )

        if not rules:

            problems.append(
                {
                    "type": "NoHTTPRouteRules",
                    "severity": "critical",
                    "message": (
                        "HTTPRoute does not define any routing rules."
                    ),
                }
            )

        # ---------------------------------------------------------------
        # Backend references
        # ---------------------------------------------------------------

        backend_count = 0

        for rule in rules:

            backend_refs = rule.get(
                "backendRefs",
                [],
            )

            backend_count += len(
                backend_refs
            )

        if backend_count == 0:

            problems.append(
                {
                    "type": "NoBackendReferences",
                    "severity": "critical",
                    "message": (
                        "HTTPRoute does not reference any backend Service."
                    ),
                }
            )

        # ---------------------------------------------------------------
        # Parent status
        # ---------------------------------------------------------------

        parents = status.get(
            "parents",
            [],
        )

        if not parents:

            problems.append(
                {
                    "type": "NoHTTPRouteStatus",
                    "severity": "warning",
                    "message": (
                        "HTTPRoute does not currently contain "
                        "parent status information."
                    ),
                }
            )

        for parent in parents:

            for condition in parent.get(
                "conditions",
                [],
            ):

                condition_type = condition.get(
                    "type"
                )

                condition_status = condition.get(
                    "status"
                )

                if (
                    condition_type == "Accepted"
                    and condition_status != "True"
                ):

                    problems.append(
                        {
                            "type": "HTTPRouteNotAccepted",
                            "severity": "critical",
                            "reason": condition.get(
                                "reason"
                            ),
                            "message": condition.get(
                                "message"
                            ),
                        }
                    )

                if (
                    condition_type == "ResolvedRefs"
                    and condition_status != "True"
                ):

                    problems.append(
                        {
                            "type": "HTTPRouteReferenceError",
                            "severity": "critical",
                            "reason": condition.get(
                                "reason"
                            ),
                            "message": condition.get(
                                "message"
                            ),
                        }
                    )

        return {
            "success": True,
            "namespace": namespace,
            "httproute": httproute_name,
            "problem_count": len(problems),
            "problems": problems,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Gateway -> HTTPRoute Investigation
# ---------------------------------------------------------------------------


def investigate_gateway_routes(
    namespace: str,
    gateway_name: str,
) -> dict[str, Any]:
    """
    Investigate the relationship between a Gateway and HTTPRoutes.

    Investigation:

        Gateway
           ↓
        Listeners
           ↓
        HTTPRoutes
           ↓
        Backend Services

    This is useful for:
    - HTTP 404
    - HTTP 502
    - HTTP 503
    - Gateway not routing
    - hostname mismatch
    - route attachment issues
    """

    try:
        gateway_result = inspect_gateway(
            namespace=namespace,
            gateway_name=gateway_name,
        )

        if not gateway_result.get("success"):
            return gateway_result

        listener_result = get_gateway_listeners(
            namespace=namespace,
            gateway_name=gateway_name,
        )

        route_result = list_httproutes(
            namespace=namespace,
        )

        gateway = gateway_result.get(
            "gateway",
            {},
        )

        attached_routes = []

        for route in route_result.get(
            "httproutes",
            [],
        ):

            for parent_ref in route.get(
                "parent_refs",
                [],
            ):

                parent_name = parent_ref.get(
                    "name"
                )

                parent_namespace = parent_ref.get(
                    "namespace",
                    namespace,
                )

                if (
                    parent_name == gateway_name
                    and parent_namespace == namespace
                ):

                    attached_routes.append(
                        route
                    )

        return {
            "success": True,
            "namespace": namespace,
            "gateway": gateway_name,
            "gateway_details": gateway,
            "listeners": listener_result.get(
                "listeners",
                [],
            ),
            "attached_httproutes": attached_routes,
            "attached_route_count": len(
                attached_routes
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Full Gateway Connectivity Investigation
# ---------------------------------------------------------------------------


def investigate_gateway_connectivity(
    namespace: str,
    gateway_name: str,
) -> dict[str, Any]:
    """
    Perform a combined Gateway API investigation.

    Investigation chain:

        GatewayClass
             ↓
          Gateway
             ↓
          Listener
             ↓
         HTTPRoute
             ↓
          Service
             ↓
         Endpoints

    This function only gathers evidence.
    It does not modify any Kubernetes resources.
    """

    try:

        gateway_result = inspect_gateway(
            namespace=namespace,
            gateway_name=gateway_name,
        )

        if not gateway_result.get("success"):
            return gateway_result

        gateway = gateway_result.get(
            "gateway",
            {},
        )

        gateway_class_name = gateway.get(
            "gateway_class_name"
        )

        gatewayclass_result = None

        if gateway_class_name:

            gatewayclass_result = (
                inspect_gatewayclass(
                    gateway_class_name
                )
            )

        listener_result = get_gateway_listeners(
            namespace=namespace,
            gateway_name=gateway_name,
        )

        gateway_problem_result = (
            detect_gateway_problems(
                namespace=namespace,
                gateway_name=gateway_name,
            )
        )

        route_result = investigate_gateway_routes(
            namespace=namespace,
            gateway_name=gateway_name,
        )

        attached_routes = route_result.get(
            "attached_httproutes",
            [],
        )

        route_investigations = []

        for route in attached_routes:

            route_name = route.get(
                "name"
            )

            if not route_name:
                continue

            route_status = get_httproute_status(
                namespace=namespace,
                httproute_name=route_name,
            )

            route_backends = get_httproute_backends(
                namespace=namespace,
                httproute_name=route_name,
            )

            route_problems = detect_httproute_problems(
                namespace=namespace,
                httproute_name=route_name,
            )

            route_investigations.append(
                {
                    "httproute": route_name,
                    "status": route_status,
                    "backends": route_backends,
                    "problems": route_problems,
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "gateway": gateway_name,
            "gatewayclass": gatewayclass_result,
            "gateway": gateway_result,
            "listeners": listener_result,
            "gateway_problems": gateway_problem_result,
            "routes": route_investigations,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Serialization Helpers
# ---------------------------------------------------------------------------


def _serialize_gateway(
    gateway: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a Gateway API object into a compact diagnostic structure.
    """

    metadata = gateway.get(
        "metadata",
        {},
    )

    spec = gateway.get(
        "spec",
        {},
    )

    status = gateway.get(
        "status",
        {},
    )

    listeners = []

    for listener in spec.get(
        "listeners",
        [],
    ):

        listeners.append(
            {
                "name": listener.get("name"),
                "hostname": listener.get(
                    "hostname"
                ),
                "port": listener.get(
                    "port"
                ),
                "protocol": listener.get(
                    "protocol"
                ),
                "tls": listener.get(
                    "tls"
                ),
                "allowed_routes": listener.get(
                    "allowedRoutes"
                ),
            }
        )

    return {
        "name": metadata.get(
            "name"
        ),
        "namespace": metadata.get(
            "namespace"
        ),
        "gateway_class_name": spec.get(
            "gatewayClassName"
        ),
        "addresses": status.get(
            "addresses",
            [],
        ),
        "listeners": listeners,
        "conditions": status.get(
            "conditions",
            [],
        ),
        "status_listeners": status.get(
            "listeners",
            [],
        ),
        "labels": metadata.get(
            "labels",
            {},
        ),
        "annotations": metadata.get(
            "annotations",
            {},
        ),
    }


def _serialize_httproute(
    route: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert an HTTPRoute object into a compact diagnostic structure.
    """

    metadata = route.get(
        "metadata",
        {},
    )

    spec = route.get(
        "spec",
        {},
    )

    status = route.get(
        "status",
        {},
    )

    rules = []

    for rule in spec.get(
        "rules",
        [],
    ):

        backend_refs = []

        for backend in rule.get(
            "backendRefs",
            [],
        ):

            backend_refs.append(
                {
                    "name": backend.get(
                        "name"
                    ),
                    "namespace": backend.get(
                        "namespace"
                    ),
                    "port": backend.get(
                        "port"
                    ),
                    "weight": backend.get(
                        "weight"
                    ),
                    "kind": backend.get(
                        "kind",
                        "Service",
                    ),
                }
            )

        rules.append(
            {
                "matches": rule.get(
                    "matches",
                    [],
                ),
                "filters": rule.get(
                    "filters",
                    [],
                ),
                "backend_refs": backend_refs,
                "timeouts": rule.get(
                    "timeouts"
                ),
            }
        )

    return {
        "name": metadata.get(
            "name"
        ),
        "namespace": metadata.get(
            "namespace"
        ),
        "hostnames": spec.get(
            "hostnames",
            [],
        ),
        "parent_refs": spec.get(
            "parentRefs",
            [],
        ),
        "rules": rules,
        "parents": status.get(
            "parents",
            [],
        ),
        "labels": metadata.get(
            "labels",
            {},
        ),
        "annotations": metadata.get(
            "annotations",
            {},
        ),
    }


# ---------------------------------------------------------------------------
# Error Helpers
# ---------------------------------------------------------------------------


def _api_error(
    error: ApiException,
) -> dict[str, Any]:
    """
    Convert Kubernetes API errors into safe dictionaries.
    """

    return {
        "success": False,
        "error": (
            f"Kubernetes API error: "
            f"{error.reason}"
        ),
        "status_code": getattr(
            error,
            "status",
            None,
        ),
    }


def _unexpected_error(
    error: Exception,
) -> dict[str, Any]:
    """
    Convert unexpected errors into safe dictionaries.
    """

    return {
        "success": False,
        "error": (
            f"Unexpected error: "
            f"{str(error)}"
        ),
    }