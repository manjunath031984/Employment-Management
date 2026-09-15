"""
Pod troubleshooting tools for the AI Infrastructure Troubleshooting Agent.

Responsibilities:
- Inspect pod status
- Inspect container status
- Inspect pod conditions
- Inspect pod logs
- Inspect pod events
- Detect common pod failure conditions
- Provide read-only troubleshooting information

IMPORTANT:
This module is READ-ONLY.

It does NOT:
- restart pods
- delete pods
- modify pods
- scale workloads
- modify deployments
- modify Kubernetes resources
"""

from __future__ import annotations

from typing import Any

from kubernetes.client import ApiException

from app.kubernetes.client import get_kubernetes_clients


# ---------------------------------------------------------------------------
# Pod Status
# ---------------------------------------------------------------------------


def inspect_pod(
    namespace: str,
    pod_name: str,
) -> dict[str, Any]:
    """
    Inspect a specific Kubernetes pod.

    This is the primary pod diagnostic function.

    It collects:
    - Pod phase
    - Pod IP
    - Node
    - Labels
    - Container information
    - Container states
    - Restart counts
    - Pod conditions
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        pod = core_v1.read_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )

        containers = []

        for container in pod.spec.containers or []:

            containers.append(
                {
                    "name": container.name,
                    "image": container.image,
                    "image_pull_policy": container.image_pull_policy,
                    "resources": _serialize_resources(
                        container.resources
                    ),
                    "ports": _serialize_ports(
                        container.ports
                    ),
                }
            )

        container_statuses = []

        for status in pod.status.container_statuses or []:

            container_statuses.append(
                {
                    "name": status.name,
                    "ready": status.ready,
                    "restart_count": status.restart_count,
                    "started": status.started,
                    "image": status.image,
                    "image_id": status.image_id,
                    "state": _serialize_container_state(
                        status.state
                    ),
                    "last_state": _serialize_container_state(
                        status.last_state
                    ),
                }
            )

        conditions = []

        for condition in pod.status.conditions or []:

            conditions.append(
                {
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message,
                    "last_transition_time": (
                        condition.last_transition_time.isoformat()
                        if condition.last_transition_time
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "pod": {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": (
                    pod.status.phase
                    if pod.status
                    else None
                ),
                "pod_ip": (
                    pod.status.pod_ip
                    if pod.status
                    else None
                ),
                "host_ip": (
                    pod.status.host_ip
                    if pod.status
                    else None
                ),
                "node_name": (
                    pod.spec.node_name
                    if pod.spec
                    else None
                ),
                "service_account": (
                    pod.spec.service_account_name
                    if pod.spec
                    else None
                ),
                "labels": pod.metadata.labels or {},
                "annotations": pod.metadata.annotations or {},
                "containers": containers,
                "container_statuses": container_statuses,
                "conditions": conditions,
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Pod List
# ---------------------------------------------------------------------------


def list_pods(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    List pods in a namespace.

    If namespace is None, pods from all namespaces are returned.
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        if namespace:
            response = core_v1.list_namespaced_pod(
                namespace=namespace
            )
        else:
            response = core_v1.list_pod_for_all_namespaces()

        pods = []

        for pod in response.items:

            pods.append(
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "phase": (
                        pod.status.phase
                        if pod.status
                        else None
                    ),
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
                    "restart_count": _get_total_restart_count(
                        pod
                    ),
                    "ready": _is_pod_ready(pod),
                }
            )

        return {
            "success": True,
            "count": len(pods),
            "pods": pods,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Pod Logs
# ---------------------------------------------------------------------------


def get_pod_logs(
    namespace: str,
    pod_name: str,
    container: str | None = None,
    tail_lines: int = 200,
    previous: bool = False,
) -> dict[str, Any]:
    """
    Retrieve pod logs.

    Args:
        namespace:
            Kubernetes namespace.

        pod_name:
            Name of the pod.

        container:
            Optional container name.

        tail_lines:
            Number of log lines to retrieve.

        previous:
            Retrieve logs from the previous terminated container.

            This is especially useful for:
            - CrashLoopBackOff
            - container crashes
            - startup failures
            - OOMKilled investigation
    """

    # Prevent excessive log retrieval.

    tail_lines = max(
        1,
        min(tail_lines, 1000),
    )

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        logs = core_v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines,
            previous=previous,
            timestamps=True,
        )

        return {
            "success": True,
            "namespace": namespace,
            "pod": pod_name,
            "container": container,
            "previous": previous,
            "tail_lines": tail_lines,
            "logs": logs,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Pod Events
# ---------------------------------------------------------------------------


def get_pod_events(
    namespace: str,
    pod_name: str,
) -> dict[str, Any]:
    """
    Get Kubernetes events related to a specific pod.

    Useful for diagnosing:
    - FailedScheduling
    - ImagePullBackOff
    - ErrImagePull
    - FailedMount
    - Unhealthy
    - BackOff
    - OOM-related failures
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        response = core_v1.list_namespaced_event(
            namespace=namespace,
        )

        events = []

        for event in response.items:

            involved_object = event.involved_object

            if not involved_object:
                continue

            if involved_object.kind != "Pod":
                continue

            if involved_object.name != pod_name:
                continue

            events.append(
                {
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "count": event.count,
                    "source": (
                        event.source.component
                        if event.source
                        else None
                    ),
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

        # Kubernetes events are often more useful when newest
        # events appear first.

        events.reverse()

        return {
            "success": True,
            "namespace": namespace,
            "pod": pod_name,
            "count": len(events),
            "events": events,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Pod Diagnosis Signals
# ---------------------------------------------------------------------------


def detect_pod_problems(
    namespace: str,
    pod_name: str,
) -> dict[str, Any]:
    """
    Detect common Kubernetes pod failure conditions.

    This function does NOT attempt to determine the final root cause.

    It identifies diagnostic signals that can be passed to the
    LangGraph diagnosis node.
    """

    try:
        clients = get_kubernetes_clients()

        core_v1 = clients["core_v1"]

        pod = core_v1.read_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )

        problems: list[dict[str, Any]] = []

        phase = (
            pod.status.phase
            if pod.status
            else None
        )

        # ---------------------------------------------------------------
        # Pod phase
        # ---------------------------------------------------------------

        if phase == "Pending":

            problems.append(
                {
                    "type": "PodPending",
                    "severity": "warning",
                    "message": (
                        "Pod is Pending and has not successfully "
                        "started."
                    ),
                }
            )

        elif phase == "Failed":

            problems.append(
                {
                    "type": "PodFailed",
                    "severity": "critical",
                    "message": (
                        "Pod is in Failed state."
                    ),
                }
            )

        # ---------------------------------------------------------------
        # Container states
        # ---------------------------------------------------------------

        for status in pod.status.container_statuses or []:

            state = status.state

            if state and state.waiting:

                reason = state.waiting.reason
                message = state.waiting.message

                if reason:

                    severity = "warning"

                    if reason in {
                        "CrashLoopBackOff",
                        "ImagePullBackOff",
                        "ErrImagePull",
                    }:
                        severity = "critical"

                    problems.append(
                        {
                            "type": reason,
                            "severity": severity,
                            "container": status.name,
                            "message": message,
                        }
                    )

            # -----------------------------------------------------------
            # Terminated container
            # -----------------------------------------------------------

            if state and state.terminated:

                reason = state.terminated.reason
                exit_code = state.terminated.exit_code

                if reason == "OOMKilled":

                    problems.append(
                        {
                            "type": "OOMKilled",
                            "severity": "critical",
                            "container": status.name,
                            "message": (
                                "Container was terminated because "
                                "it exceeded its memory limit."
                            ),
                            "exit_code": exit_code,
                        }
                    )

                elif exit_code and exit_code != 0:

                    problems.append(
                        {
                            "type": "ContainerTerminated",
                            "severity": "critical",
                            "container": status.name,
                            "reason": reason,
                            "exit_code": exit_code,
                            "message": (
                                state.terminated.message
                            ),
                        }
                    )

            # -----------------------------------------------------------
            # Restart count
            # -----------------------------------------------------------

            if status.restart_count > 0:

                problems.append(
                    {
                        "type": "ContainerRestarts",
                        "severity": "warning",
                        "container": status.name,
                        "restart_count": status.restart_count,
                        "message": (
                            f"Container has restarted "
                            f"{status.restart_count} time(s)."
                        ),
                    }
                )

        # ---------------------------------------------------------------
        # Pod conditions
        # ---------------------------------------------------------------

        for condition in pod.status.conditions or []:

            if (
                condition.type == "Ready"
                and condition.status != "True"
            ):

                problems.append(
                    {
                        "type": "PodNotReady",
                        "severity": "warning",
                        "message": (
                            condition.message
                            or "Pod is not Ready."
                        ),
                        "reason": condition.reason,
                    }
                )

            if (
                condition.type == "ContainersReady"
                and condition.status != "True"
            ):

                problems.append(
                    {
                        "type": "ContainersNotReady",
                        "severity": "warning",
                        "message": (
                            condition.message
                            or "One or more containers are not ready."
                        ),
                        "reason": condition.reason,
                    }
                )

        return {
            "success": True,
            "namespace": namespace,
            "pod": pod_name,
            "phase": phase,
            "problem_count": len(problems),
            "problems": problems,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Container Information
# ---------------------------------------------------------------------------


def get_container_status(
    namespace: str,
    pod_name: str,
) -> dict[str, Any]:
    """
    Return detailed container status information for a pod.
    """

    try:
        clients = get_kubernetes_clients()

        pod = clients["core_v1"].read_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )

        statuses = []

        for status in pod.status.container_statuses or []:

            statuses.append(
                {
                    "name": status.name,
                    "ready": status.ready,
                    "started": status.started,
                    "restart_count": status.restart_count,
                    "image": status.image,
                    "image_id": status.image_id,
                    "state": _serialize_container_state(
                        status.state
                    ),
                    "last_state": _serialize_container_state(
                        status.last_state
                    ),
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "pod": pod_name,
            "containers": statuses,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Readiness
# ---------------------------------------------------------------------------


def check_pod_readiness(
    namespace: str,
    pod_name: str,
) -> dict[str, Any]:
    """
    Check whether a pod is Ready.
    """

    try:
        clients = get_kubernetes_clients()

        pod = clients["core_v1"].read_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )

        ready = _is_pod_ready(pod)

        return {
            "success": True,
            "namespace": namespace,
            "pod": pod_name,
            "ready": ready,
            "phase": (
                pod.status.phase
                if pod.status
                else None
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def _is_pod_ready(pod: Any) -> bool:
    """
    Determine whether a Kubernetes pod is Ready.
    """

    if not pod.status:
        return False

    for condition in pod.status.conditions or []:

        if condition.type == "Ready":

            return condition.status == "True"

    return False


def _get_total_restart_count(pod: Any) -> int:
    """
    Calculate total container restart count.
    """

    total = 0

    for status in pod.status.container_statuses or []:
        total += status.restart_count or 0

    return total


def _serialize_container_state(
    state: Any,
) -> dict[str, Any]:
    """
    Convert Kubernetes container state into a JSON-safe dictionary.
    """

    if not state:
        return {}

    if state.running:

        return {
            "type": "running",
            "started_at": (
                state.running.started_at.isoformat()
                if state.running.started_at
                else None
            ),
            "finished_at": None,
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
            "message": state.terminated.message,
            "exit_code": state.terminated.exit_code,
            "signal": state.terminated.signal,
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


def _serialize_resources(
    resources: Any,
) -> dict[str, Any]:
    """
    Serialize Kubernetes resource requests and limits.
    """

    if not resources:
        return {}

    return {
        "requests": resources.requests or {},
        "limits": resources.limits or {},
    }


def _serialize_ports(
    ports: Any,
) -> list[dict[str, Any]]:
    """
    Serialize container ports.
    """

    if not ports:
        return []

    return [
        {
            "name": port.name,
            "container_port": port.container_port,
            "protocol": port.protocol,
        }
        for port in ports
    ]


def _api_error(
    error: ApiException,
) -> dict[str, Any]:
    """
    Convert Kubernetes API errors into safe dictionaries.
    """

    return {
        "success": False,
        "error": f"Kubernetes API error: {error.reason}",
        "status_code": getattr(error, "status", None),
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