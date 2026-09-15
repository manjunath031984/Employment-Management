"""
Service troubleshooting tools for the AI Infrastructure Troubleshooting Agent.

Responsibilities:
- Inspect Kubernetes Services
- List Services
- Inspect Service selectors
- Inspect Service ports
- Inspect Service endpoints
- Detect missing/unready endpoints
- Compare Service selectors with backend Pods
- Diagnose common Service connectivity problems

IMPORTANT:
This module is READ-ONLY.

It does NOT:
- create Services
- update Services
- delete Services
- modify selectors
- modify ports
- modify endpoints
"""

from __future__ import annotations

from typing import Any

from kubernetes.client import ApiException

from app.kubernetes.client import get_kubernetes_clients


# ---------------------------------------------------------------------------
# Service Inspection
# ---------------------------------------------------------------------------


def inspect_service(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Inspect a specific Kubernetes Service.

    Collects:
    - Service type
    - Cluster IP
    - External IPs
    - Selector
    - Ports
    - Session affinity
    - Health check information
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        service = core_v1.read_namespaced_service(
            name=service_name,
            namespace=namespace,
        )

        spec = service.spec

        ports = []

        for port in spec.ports or []:

            ports.append(
                {
                    "name": port.name,
                    "port": port.port,
                    "target_port": str(port.target_port),
                    "protocol": port.protocol,
                    "node_port": port.node_port,
                    "app_protocol": port.app_protocol,
                }
            )

        return {
            "success": True,
            "service": {
                "name": service.metadata.name,
                "namespace": service.metadata.namespace,
                "type": spec.type if spec else None,
                "cluster_ip": (
                    spec.cluster_ip
                    if spec
                    else None
                ),
                "cluster_ips": (
                    spec.cluster_ips or []
                    if spec
                    else []
                ),
                "external_ips": (
                    spec.external_ips or []
                    if spec
                    else []
                ),
                "external_name": (
                    spec.external_name
                    if spec
                    else None
                ),
                "selector": (
                    spec.selector or {}
                    if spec
                    else {}
                ),
                "ports": ports,
                "session_affinity": (
                    spec.session_affinity
                    if spec
                    else None
                ),
                "publish_not_ready_addresses": (
                    spec.publish_not_ready_addresses
                    if spec
                    else False
                ),
                "internal_traffic_policy": (
                    spec.internal_traffic_policy
                    if spec
                    else None
                ),
                "external_traffic_policy": (
                    spec.external_traffic_policy
                    if spec
                    else None
                ),
                "labels": service.metadata.labels or {},
                "annotations": service.metadata.annotations or {},
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# List Services
# ---------------------------------------------------------------------------


def list_services(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    List Kubernetes Services.

    If namespace is None, Services from all namespaces are returned.
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        if namespace:

            response = core_v1.list_namespaced_service(
                namespace=namespace
            )

        else:

            response = (
                core_v1
                .list_service_for_all_namespaces()
            )

        services = []

        for service in response.items:

            spec = service.spec

            services.append(
                {
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "type": (
                        spec.type
                        if spec
                        else None
                    ),
                    "cluster_ip": (
                        spec.cluster_ip
                        if spec
                        else None
                    ),
                    "selector": (
                        spec.selector or {}
                        if spec
                        else {}
                    ),
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "target_port": str(
                                port.target_port
                            ),
                            "protocol": port.protocol,
                        }
                        for port in (spec.ports or [])
                    ],
                }
            )

        return {
            "success": True,
            "count": len(services),
            "services": services,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Service Endpoints
# ---------------------------------------------------------------------------


def get_service_endpoints(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Inspect the Endpoints associated with a Kubernetes Service.

    This is one of the most important functions for diagnosing:

    - connection refused
    - no backend pods
    - service selector problems
    - readiness problems
    - backend availability
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        endpoint = core_v1.read_namespaced_endpoints(
            name=service_name,
            namespace=namespace,
        )

        subsets = []

        ready_addresses = []
        not_ready_addresses = []
        ports = []

        for subset in endpoint.subsets or []:

            for address in subset.addresses or []:

                ready_addresses.append(
                    {
                        "ip": address.ip,
                        "node_name": address.node_name,
                        "hostname": address.hostname,
                        "pod": (
                            address.target_ref.name
                            if address.target_ref
                            and address.target_ref.kind == "Pod"
                            else None
                        ),
                    }
                )

            for address in subset.not_ready_addresses or []:

                not_ready_addresses.append(
                    {
                        "ip": address.ip,
                        "node_name": address.node_name,
                        "hostname": address.hostname,
                        "pod": (
                            address.target_ref.name
                            if address.target_ref
                            and address.target_ref.kind == "Pod"
                            else None
                        ),
                    }
                )

            for port in subset.ports or []:

                ports.append(
                    {
                        "name": port.name,
                        "port": port.port,
                        "protocol": port.protocol,
                    }
                )

            subsets.append(
                {
                    "addresses": [
                        {
                            "ip": address.ip,
                            "node_name": address.node_name,
                            "hostname": address.hostname,
                        }
                        for address in (
                            subset.addresses or []
                        )
                    ],
                    "not_ready_addresses": [
                        {
                            "ip": address.ip,
                            "node_name": address.node_name,
                            "hostname": address.hostname,
                        }
                        for address in (
                            subset.not_ready_addresses or []
                        )
                    ],
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "protocol": port.protocol,
                        }
                        for port in (
                            subset.ports or []
                        )
                    ],
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "service": service_name,
            "ready_endpoint_count": len(
                ready_addresses
            ),
            "not_ready_endpoint_count": len(
                not_ready_addresses
            ),
            "ready_endpoints": ready_addresses,
            "not_ready_endpoints": not_ready_addresses,
            "ports": ports,
            "subsets": subsets,
            "has_ready_endpoints": (
                len(ready_addresses) > 0
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Service Problems
# ---------------------------------------------------------------------------


def detect_service_problems(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Detect common Kubernetes Service problems.

    This function identifies diagnostic signals.

    It does NOT determine the final root cause.
    """

    try:
        clients = get_kubernetes_clients()
        core_v1 = clients["core_v1"]

        service = core_v1.read_namespaced_service(
            name=service_name,
            namespace=namespace,
        )

        endpoint = core_v1.read_namespaced_endpoints(
            name=service_name,
            namespace=namespace,
        )

        problems: list[dict[str, Any]] = []
        spec = service.spec

        # ---------------------------------------------------------------
        # Service selector
        # ---------------------------------------------------------------

        selector = spec.selector if spec else None

        if not selector:
            problems.append(
                {
                    "type": "MissingServiceSelector",
                    "severity": "warning",
                    "message": (
                        "Service does not have a selector. "
                        "Backend endpoints may need to be managed "
                        "through another mechanism."
                    ),
                }
            )

        # ---------------------------------------------------------------
        # Service ports
        # ---------------------------------------------------------------

        if not spec or not spec.ports:
            problems.append(
                {
                    "type": "MissingServicePort",
                    "severity": "critical",
                    "message": "Service does not define any ports.",
                }
            )

        # ---------------------------------------------------------------
        # Endpoints
        # ---------------------------------------------------------------

        ready_endpoint_count = 0
        not_ready_endpoint_count = 0

        for subset in endpoint.subsets or []:
            ready_endpoint_count += len(subset.addresses or [])
            not_ready_endpoint_count += len(
                subset.not_ready_addresses or []
            )

        if ready_endpoint_count == 0:
            if not_ready_endpoint_count > 0:
                problems.append(
                    {
                        "type": "NoReadyEndpoints",
                        "severity": "critical",
                        "message": (
                            "Service has backend endpoints, "
                            "but none of them are Ready."
                        ),
                        "not_ready_endpoints": not_ready_endpoint_count,
                    }
                )
            else:
                problems.append(
                    {
                        "type": "NoEndpoints",
                        "severity": "critical",
                        "message": (
                            "Service does not have any backend endpoints."
                        ),
                    }
                )

        return {
            "success": True,
            "namespace": namespace,
            "service": service_name,
            "problems": problems,
            "ready_endpoint_count": ready_endpoint_count,
            "not_ready_endpoint_count": not_ready_endpoint_count,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Service Selector Investigation
# ---------------------------------------------------------------------------


def inspect_service_selector(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Compare a Service selector against Pods in the same namespace.

    This helps identify:

        Service selector
              ↓
        matching Pods
              ↓
        Ready Pods
              ↓
        Service endpoints

    Common problem:
    Service selector does not match Deployment/Pod labels.
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        service = core_v1.read_namespaced_service(
            name=service_name,
            namespace=namespace,
        )

        selector = (
            service.spec.selector
            if service.spec
            else {}
        )

        if not selector:

            return {
                "success": True,
                "namespace": namespace,
                "service": service_name,
                "selector": {},
                "matching_pods": [],
                "matching_pod_count": 0,
                "message": (
                    "Service does not define a selector."
                ),
            }

        label_selector = ",".join(
            f"{key}={value}"
            for key, value in selector.items()
        )

        pods = core_v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector,
        )

        matching_pods = []

        for pod in pods.items:

            matching_pods.append(
                {
                    "name": pod.metadata.name,
                    "phase": (
                        pod.status.phase
                        if pod.status
                        else None
                    ),
                    "ready": _is_pod_ready(pod),
                    "pod_ip": (
                        pod.status.pod_ip
                        if pod.status
                        else None
                    ),
                    "node_name": (
                        pod.spec.node_name
                        if pod.spec
                        else None
                    ),
                    "labels": pod.metadata.labels or {},
                }
            )

        ready_pods = [
            pod
            for pod in matching_pods
            if pod["ready"]
        ]

        return {
            "success": True,
            "namespace": namespace,
            "service": service_name,
            "selector": selector,
            "label_selector": label_selector,
            "matching_pod_count": len(
                matching_pods
            ),
            "ready_pod_count": len(
                ready_pods
            ),
            "matching_pods": matching_pods,
            "has_matching_pods": (
                len(matching_pods) > 0
            ),
            "has_ready_pods": (
                len(ready_pods) > 0
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Service Port Validation
# ---------------------------------------------------------------------------


def validate_service_ports(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Validate basic Service port configuration.

    Checks:
    - Service ports
    - Target ports
    - Matching container ports on selected Pods

    This is a diagnostic check and does not modify anything.
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        service = core_v1.read_namespaced_service(
            name=service_name,
            namespace=namespace,
        )

        spec = service.spec

        selector = (
            spec.selector
            if spec
            else {}
        )

        if not selector:

            return {
                "success": True,
                "namespace": namespace,
                "service": service_name,
                "valid": False,
                "message": (
                    "Cannot validate target ports because "
                    "the Service has no selector."
                ),
            }

        label_selector = ",".join(
            f"{key}={value}"
            for key, value in selector.items()
        )

        pods = core_v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector,
        )

        pod_port_map: dict[str, list[int]] = {}

        for pod in pods.items:

            container_ports = []

            if pod.spec:

                for container in pod.spec.containers or []:

                    for port in container.ports or []:

                        if port.container_port:
                            container_ports.append(
                                port.container_port
                            )

            pod_port_map[pod.metadata.name] = (
                container_ports
            )

        port_results = []

        for service_port in spec.ports or []:

            target_port = service_port.target_port

            numeric_target_port = None

            if isinstance(
                target_port,
                int,
            ):
                numeric_target_port = target_port

            matching_pods = []

            for pod_name, container_ports in (
                pod_port_map.items()
            ):

                if (
                    numeric_target_port is not None
                    and numeric_target_port
                    in container_ports
                ):

                    matching_pods.append(
                        pod_name
                    )

            port_results.append(
                {
                    "service_port": service_port.port,
                    "target_port": str(
                        target_port
                    ),
                    "protocol": service_port.protocol,
                    "numeric_target_port": (
                        numeric_target_port
                    ),
                    "pods_with_matching_port": (
                        matching_pods
                    ),
                    "matching_pod_count": len(
                        matching_pods
                    ),
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "service": service_name,
            "valid": True,
            "ports": port_results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Service Connectivity Investigation
# ---------------------------------------------------------------------------


def investigate_service_connectivity(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Perform a combined read-only Service connectivity investigation.

    Investigation flow:

        Service
           ↓
        Selector
           ↓
        Matching Pods
           ↓
        Ready Pods
           ↓
        Endpoints
           ↓
        Service Ports

    This function is useful when the user reports:

    - connection refused
    - service unavailable
    - backend unavailable
    - HTTP 502/503
    - Gateway cannot reach backend
    """

    try:

        service_result = inspect_service(
            namespace=namespace,
            service_name=service_name,
        )

        if not service_result.get("success"):
            return service_result

        selector_result = inspect_service_selector(
            namespace=namespace,
            service_name=service_name,
        )

        endpoint_result = get_service_endpoints(
            namespace=namespace,
            service_name=service_name,
        )

        problem_result = detect_service_problems(
            namespace=namespace,
            service_name=service_name,
        )

        port_result = validate_service_ports(
            namespace=namespace,
            service_name=service_name,
        )

        return {
            "success": True,
            "namespace": namespace,
            "service": service_name,
            "service_details": service_result.get(
                "service"
            ),
            "selector_analysis": selector_result,
            "endpoint_analysis": endpoint_result,
            "port_analysis": port_result,
            "problem_analysis": problem_result,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def _is_pod_ready(
    pod: Any,
) -> bool:
    """
    Determine whether a Pod is Ready.
    """

    if not pod.status:
        return False

    for condition in pod.status.conditions or []:

        if condition.type == "Ready":

            return condition.status == "True"

    return False


def _api_error(
    error: ApiException,
) -> dict[str, Any]:
    """
    Convert Kubernetes API errors into safe dictionaries.
    """

    return {
        "success": False,
        "error": f"Kubernetes API error: {error.reason}",
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
        "error": f"Unexpected error: {str(error)}",
    }