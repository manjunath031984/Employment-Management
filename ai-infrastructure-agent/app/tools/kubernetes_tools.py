"""
Read-only Kubernetes tools for the AI Infrastructure Troubleshooting Agent.

Responsibilities:
- Inspect Kubernetes namespaces
- Inspect pods
- Inspect pod logs
- Inspect Kubernetes events
- Inspect deployments
- Inspect services
- Inspect endpoints
- Inspect StatefulSets
- Inspect PVCs
- Inspect Gateway API resources

IMPORTANT:
This module is READ-ONLY.

It does NOT:
- create Kubernetes resources
- update Kubernetes resources
- delete Kubernetes resources
- restart pods
- scale deployments
- modify configurations
"""

from __future__ import annotations

from typing import Any

from kubernetes.client import ApiException

from app.kubernetes.client import get_kubernetes_clients


def _api_error(error: ApiException) -> dict[str, Any]:
    """
    Convert a Kubernetes ApiException into a safe dictionary.
    """

    return {
        "success": False,
        "error": f"Kubernetes API error: {error.reason}",
        "status_code": getattr(error, "status", None),
    }


def _unexpected_error(error: Exception) -> dict[str, Any]:
    """
    Convert unexpected exceptions into a safe dictionary.
    """

    return {
        "success": False,
        "error": f"Unexpected error: {str(error)}",
    }


# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------


def get_namespaces() -> dict[str, Any]:
    """
    Get all Kubernetes namespaces.

    Returns:
        Dictionary containing namespace information.
    """

    try:
        clients = get_kubernetes_clients()

        namespaces = clients["core_v1"].list_namespace()

        results = []

        for namespace in namespaces.items:
            results.append(
                {
                    "name": namespace.metadata.name,
                    "status": namespace.status.phase
                    if namespace.status
                    else None,
                }
            )

        return {
            "success": True,
            "count": len(results),
            "namespaces": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def get_namespace(namespace: str) -> dict[str, Any]:
    """
    Get information about a specific namespace.
    """

    try:
        clients = get_kubernetes_clients()

        result = clients["core_v1"].read_namespace(name=namespace)

        return {
            "success": True,
            "namespace": {
                "name": result.metadata.name,
                "status": result.status.phase if result.status else None,
                "labels": result.metadata.labels or {},
                "annotations": result.metadata.annotations or {},
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Pods
# ---------------------------------------------------------------------------


def get_pods(namespace: str | None = None) -> dict[str, Any]:
    """
    Get pods from a namespace.

    If namespace is None, pods from all namespaces are returned.
    """

    try:
        clients = get_kubernetes_clients()

        if namespace:
            response = clients["core_v1"].list_namespaced_pod(
                namespace=namespace
            )
        else:
            response = clients["core_v1"].list_pod_for_all_namespaces()

        results = []

        for pod in response.items:
            container_statuses = []

            if pod.status and pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    container_statuses.append(
                        {
                            "name": container.name,
                            "ready": container.ready,
                            "restart_count": container.restart_count,
                            "state": _get_container_state(container),
                        }
                    )

            results.append(
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "phase": pod.status.phase if pod.status else None,
                    "pod_ip": pod.status.pod_ip if pod.status else None,
                    "node_name": (
                        pod.spec.node_name
                        if pod.spec
                        else None
                    ),
                    "labels": pod.metadata.labels or {},
                    "container_statuses": container_statuses,
                }
            )

        return {
            "success": True,
            "count": len(results),
            "pods": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def get_pod(
    namespace: str,
    pod_name: str,
) -> dict[str, Any]:
    """
    Get detailed information about a specific pod.
    """

    try:
        clients = get_kubernetes_clients()

        pod = clients["core_v1"].read_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )

        containers = []

        if pod.spec and pod.spec.containers:
            for container in pod.spec.containers:
                containers.append(
                    {
                        "name": container.name,
                        "image": container.image,
                        "image_pull_policy": container.image_pull_policy,
                        "ports": [
                            {
                                "container_port": port.container_port,
                                "protocol": port.protocol,
                            }
                            for port in (container.ports or [])
                        ],
                        "resources": (
                            container.resources.to_dict()
                            if container.resources
                            else {}
                        ),
                    }
                )

        container_statuses = []

        if pod.status and pod.status.container_statuses:
            for container in pod.status.container_statuses:
                container_statuses.append(
                    {
                        "name": container.name,
                        "ready": container.ready,
                        "restart_count": container.restart_count,
                        "state": _get_container_state(container),
                    }
                )

        return {
            "success": True,
            "pod": {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": pod.status.phase if pod.status else None,
                "pod_ip": pod.status.pod_ip if pod.status else None,
                "host_ip": pod.status.host_ip if pod.status else None,
                "node_name": (
                    pod.spec.node_name
                    if pod.spec
                    else None
                ),
                "labels": pod.metadata.labels or {},
                "annotations": pod.metadata.annotations or {},
                "containers": containers,
                "container_statuses": container_statuses,
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def get_pod_logs(
    namespace: str,
    pod_name: str,
    container: str | None = None,
    tail_lines: int = 200,
) -> dict[str, Any]:
    """
    Read pod logs.

    This is intentionally limited to a reasonable number of lines
    to prevent excessive log retrieval.
    """

    tail_lines = max(1, min(tail_lines, 1000))

    try:
        clients = get_kubernetes_clients()

        logs = clients["core_v1"].read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines,
            timestamps=True,
        )

        return {
            "success": True,
            "namespace": namespace,
            "pod": pod_name,
            "container": container,
            "tail_lines": tail_lines,
            "logs": logs,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def get_pod_events(
    namespace: str,
    pod_name: str,
) -> dict[str, Any]:
    """
    Get Kubernetes events associated with a pod.
    """

    try:
        clients = get_kubernetes_clients()

        events = clients["core_v1"].list_namespaced_event(
            namespace=namespace,
        )

        results = []

        for event in events.items:

            involved_object = event.involved_object

            if (
                involved_object
                and involved_object.name == pod_name
                and involved_object.kind == "Pod"
            ):
                results.append(
                    {
                        "type": event.type,
                        "reason": event.reason,
                        "message": event.message,
                        "count": event.count,
                        "first_timestamp": (
                            event.first_timestamp.isoformat()
                            if event.first_timestamp
                            else None
                        ),
                        "last_timestamp": (
                            event.last_timestamp.isoformat()
                            if event.last_timestamp
                            else None
                        ),
                    }
                )

        return {
            "success": True,
            "namespace": namespace,
            "pod": pod_name,
            "count": len(results),
            "events": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Deployments
# ---------------------------------------------------------------------------


def get_deployments(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    Get Kubernetes deployments.
    """

    try:
        clients = get_kubernetes_clients()

        if namespace:
            response = clients["apps_v1"].list_namespaced_deployment(
                namespace=namespace
            )
        else:
            response = clients["apps_v1"].list_deployment_for_all_namespaces()

        results = []

        for deployment in response.items:

            status = deployment.status

            results.append(
                {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "replicas": (
                        deployment.spec.replicas
                        if deployment.spec
                        else None
                    ),
                    "available_replicas": (
                        status.available_replicas
                        if status
                        else None
                    ),
                    "ready_replicas": (
                        status.ready_replicas
                        if status
                        else None
                    ),
                    "updated_replicas": (
                        status.updated_replicas
                        if status
                        else None
                    ),
                    "labels": deployment.metadata.labels or {},
                }
            )

        return {
            "success": True,
            "count": len(results),
            "deployments": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def get_deployment(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Get detailed information about a deployment.
    """

    try:
        clients = get_kubernetes_clients()

        deployment = clients["apps_v1"].read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
        )

        status = deployment.status

        return {
            "success": True,
            "deployment": {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": (
                    deployment.spec.replicas
                    if deployment.spec
                    else None
                ),
                "available_replicas": (
                    status.available_replicas
                    if status
                    else None
                ),
                "ready_replicas": (
                    status.ready_replicas
                    if status
                    else None
                ),
                "updated_replicas": (
                    status.updated_replicas
                    if status
                    else None
                ),
                "labels": deployment.metadata.labels or {},
                "selector": (
                    deployment.spec.selector.match_labels
                    if deployment.spec
                    and deployment.spec.selector
                    else {}
                ),
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------


def get_services(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    Get Kubernetes services.
    """

    try:
        clients = get_kubernetes_clients()

        if namespace:
            response = clients["core_v1"].list_namespaced_service(
                namespace=namespace
            )
        else:
            response = clients["core_v1"].list_service_for_all_namespaces()

        results = []

        for service in response.items:

            ports = []

            if service.spec and service.spec.ports:
                for port in service.spec.ports:
                    ports.append(
                        {
                            "name": port.name,
                            "port": port.port,
                            "target_port": str(port.target_port),
                            "protocol": port.protocol,
                        }
                    )

            results.append(
                {
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "type": (
                        service.spec.type
                        if service.spec
                        else None
                    ),
                    "cluster_ip": (
                        service.spec.cluster_ip
                        if service.spec
                        else None
                    ),
                    "selector": (
                        service.spec.selector
                        if service.spec
                        else {}
                    ),
                    "ports": ports,
                }
            )

        return {
            "success": True,
            "count": len(results),
            "services": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def get_service(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Get detailed information about a service.
    """

    try:
        clients = get_kubernetes_clients()

        service = clients["core_v1"].read_namespaced_service(
            name=service_name,
            namespace=namespace,
        )

        ports = []

        if service.spec and service.spec.ports:
            for port in service.spec.ports:
                ports.append(
                    {
                        "name": port.name,
                        "port": port.port,
                        "target_port": str(port.target_port),
                        "protocol": port.protocol,
                    }
                )

        return {
            "success": True,
            "service": {
                "name": service.metadata.name,
                "namespace": service.metadata.namespace,
                "type": service.spec.type if service.spec else None,
                "cluster_ip": (
                    service.spec.cluster_ip
                    if service.spec
                    else None
                ),
                "selector": (
                    service.spec.selector
                    if service.spec
                    else {}
                ),
                "ports": ports,
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


def get_endpoints(
    namespace: str,
    service_name: str,
) -> dict[str, Any]:
    """
    Get endpoints for a Kubernetes service.

    Useful for diagnosing:
    - connection refused
    - no backend pods
    - readiness issues
    - service selector problems
    """

    try:
        clients = get_kubernetes_clients()

        endpoint = clients["core_v1"].read_namespaced_endpoints(
            name=service_name,
            namespace=namespace,
        )

        subsets = []

        for subset in endpoint.subsets or []:

            addresses = []

            for address in subset.addresses or []:
                addresses.append(
                    {
                        "ip": address.ip,
                        "node_name": address.node_name,
                        "target_ref": (
                            address.target_ref.name
                            if address.target_ref
                            else None
                        ),
                    }
                )

            not_ready_addresses = []

            for address in subset.not_ready_addresses or []:
                not_ready_addresses.append(
                    {
                        "ip": address.ip,
                        "node_name": address.node_name,
                        "target_ref": (
                            address.target_ref.name
                            if address.target_ref
                            else None
                        ),
                    }
                )

            ports = []

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
                    "addresses": addresses,
                    "not_ready_addresses": not_ready_addresses,
                    "ports": ports,
                }
            )

        return {
            "success": True,
            "service": service_name,
            "namespace": namespace,
            "subsets": subsets,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# StatefulSets
# ---------------------------------------------------------------------------


def get_statefulsets(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    Get Kubernetes StatefulSets.
    """

    try:
        clients = get_kubernetes_clients()

        if namespace:
            response = clients["apps_v1"].list_namespaced_stateful_set(
                namespace=namespace
            )
        else:
            response = (
                clients["apps_v1"]
                .list_stateful_set_for_all_namespaces()
            )

        results = []

        for statefulset in response.items:

            status = statefulset.status

            results.append(
                {
                    "name": statefulset.metadata.name,
                    "namespace": statefulset.metadata.namespace,
                    "replicas": (
                        statefulset.spec.replicas
                        if statefulset.spec
                        else None
                    ),
                    "ready_replicas": (
                        status.ready_replicas
                        if status
                        else None
                    ),
                    "current_replicas": (
                        status.current_replicas
                        if status
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "count": len(results),
            "statefulsets": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# PersistentVolumeClaims
# ---------------------------------------------------------------------------


def get_pvcs(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    Get PersistentVolumeClaims.
    """

    try:
        clients = get_kubernetes_clients()

        if namespace:
            response = clients["core_v1"].list_namespaced_persistent_volume_claim(
                namespace=namespace
            )
        else:
            response = (
                clients["core_v1"]
                .list_persistent_volume_claim_for_all_namespaces()
            )

        results = []

        for pvc in response.items:

            results.append(
                {
                    "name": pvc.metadata.name,
                    "namespace": pvc.metadata.namespace,
                    "status": (
                        pvc.status.phase
                        if pvc.status
                        else None
                    ),
                    "storage_class": (
                        pvc.spec.storage_class_name
                        if pvc.spec
                        else None
                    ),
                    "requested_storage": (
                        pvc.spec.resources.requests.get("storage")
                        if pvc.spec
                        and pvc.spec.resources
                        and pvc.spec.resources.requests
                        else None
                    ),
                    "volume_name": (
                        pvc.spec.volume_name
                        if pvc.spec
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "count": len(results),
            "pvcs": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Gateway API
# ---------------------------------------------------------------------------


def get_gateways(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    Get Gateway API Gateway resources.

    Requires Gateway API CRDs to be installed in the cluster.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        if namespace:
            response = custom_objects.list_namespaced_custom_object(
                group="gateway.networking.k8s.io",
                version="v1",
                namespace=namespace,
                plural="gateways",
            )
        else:
            response = custom_objects.list_cluster_custom_object(
                group="gateway.networking.k8s.io",
                version="v1",
                plural="gateways",
            )

        gateways = []

        for item in response.get("items", []):

            status = item.get("status", {})
            spec = item.get("spec", {})

            gateways.append(
                {
                    "name": item.get("metadata", {}).get("name"),
                    "namespace": item.get("metadata", {}).get("namespace"),
                    "gateway_class_name": spec.get(
                        "gatewayClassName"
                    ),
                    "listeners": spec.get("listeners", []),
                    "addresses": status.get("addresses", []),
                    "conditions": status.get("conditions", []),
                }
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


def get_httproutes(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    Get Gateway API HTTPRoute resources.
    """

    try:
        clients = get_kubernetes_clients()

        custom_objects = clients["custom_objects"]

        if namespace:
            response = custom_objects.list_namespaced_custom_object(
                group="gateway.networking.k8s.io",
                version="v1",
                namespace=namespace,
                plural="httproutes",
            )
        else:
            response = custom_objects.list_cluster_custom_object(
                group="gateway.networking.k8s.io",
                version="v1",
                plural="httproutes",
            )

        routes = []

        for item in response.get("items", []):

            spec = item.get("spec", {})
            status = item.get("status", {})

            routes.append(
                {
                    "name": item.get("metadata", {}).get("name"),
                    "namespace": item.get("metadata", {}).get("namespace"),
                    "hostnames": spec.get("hostnames", []),
                    "parent_refs": spec.get("parentRefs", []),
                    "rules": spec.get("rules", []),
                    "parents": status.get("parents", []),
                }
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


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _get_container_state(container_status: Any) -> dict[str, Any]:
    """
    Convert Kubernetes container state into a simple dictionary.
    """

    state = container_status.state

    if state is None:
        return {}

    if state.running:
        return {
            "type": "running",
            "started_at": (
                state.running.started_at.isoformat()
                if state.running.started_at
                else None
            ),
        }

    if state.waiting:
        return {
            "type": "waiting",
            "reason": state.waiting.reason,
            "message": state.waiting.message,
        }

    if state.terminated:
        return {
            "type": "terminated",
            "reason": state.terminated.reason,
            "exit_code": state.terminated.exit_code,
            "signal": state.terminated.signal,
            "message": state.terminated.message,
            "started_at": (
                state.terminated.started_at.isoformat()
                if state.terminated.started_at
                else None
            ),
            "finished_at": (
                state.terminated.finished_at.isoformat()
                if state.terminated.finished_at
                else None
            ),
        }

    return {}