"""
Deployment troubleshooting tools for the AI Infrastructure Troubleshooting Agent.

Responsibilities:
- Inspect Kubernetes Deployments
- Check replica status
- Check rollout status
- Inspect Deployment conditions
- Inspect Deployment strategy
- Inspect Deployment selectors
- Inspect container images
- Detect common Deployment problems
- Inspect ReplicaSets associated with a Deployment

IMPORTANT:
This module is READ-ONLY.

It does NOT:
- scale deployments
- restart deployments
- update deployments
- delete deployments
- modify Kubernetes resources
"""

from __future__ import annotations

from typing import Any

from kubernetes.client import ApiException
from app.kubernetes.client import get_kubernetes_clients


# ---------------------------------------------------------------------------
# Deployment Inspection
# ---------------------------------------------------------------------------


def inspect_deployment(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Inspect a specific Kubernetes Deployment.

    Collects:
    - Replica configuration
    - Available/ready replicas
    - Deployment conditions
    - Selector
    - Pod template
    - Container images
    - Resource requests/limits
    - Deployment strategy
    """

    try:
        clients = get_kubernetes_clients()

        apps_v1 = clients["apps_v1"]

        deployment = apps_v1.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
        )

        spec = deployment.spec
        status = deployment.status

        containers = []

        if spec and spec.template and spec.template.spec:

            for container in spec.template.spec.containers or []:

                containers.append(
                    {
                        "name": container.name,
                        "image": container.image,
                        "image_pull_policy": (
                            container.image_pull_policy
                        ),
                        "ports": _serialize_ports(
                            container.ports
                        ),
                        "resources": _serialize_resources(
                            container.resources
                        ),
                        "env_variables": _serialize_env_names(
                            container.env
                        ),
                    }
                )

        conditions = []

        if status:

            for condition in status.conditions or []:

                conditions.append(
                    {
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message,
                        "last_update_time": (
                            condition.last_update_time.isoformat()
                            if condition.last_update_time
                            else None
                        ),
                        "last_transition_time": (
                            condition.last_transition_time.isoformat()
                            if condition.last_transition_time
                            else None
                        ),
                    }
                )

        return {
            "success": True,
            "deployment": {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "generation": deployment.metadata.generation,
                "observed_generation": (
                    status.observed_generation
                    if status
                    else None
                ),
                "replicas": (
                    spec.replicas
                    if spec
                    else None
                ),
                "updated_replicas": (
                    status.updated_replicas
                    if status
                    else None
                ),
                "ready_replicas": (
                    status.ready_replicas
                    if status
                    else None
                ),
                "available_replicas": (
                    status.available_replicas
                    if status
                    else None
                ),
                "unavailable_replicas": (
                    status.unavailable_replicas
                    if status
                    else None
                ),
                "selector": _serialize_selector(
                    spec.selector
                    if spec
                    else None
                ),
                "strategy": _serialize_strategy(
                    spec.strategy
                    if spec
                    else None
                ),
                "min_ready_seconds": (
                    spec.min_ready_seconds
                    if spec
                    else None
                ),
                "revision_history_limit": (
                    spec.revision_history_limit
                    if spec
                    else None
                ),
                "containers": containers,
                "conditions": conditions,
                "labels": deployment.metadata.labels or {},
                "annotations": deployment.metadata.annotations or {},
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# List Deployments
# ---------------------------------------------------------------------------


def list_deployments(
    namespace: str | None = None,
) -> dict[str, Any]:
    """
    List Kubernetes Deployments.

    If namespace is None, Deployments from all namespaces
    are returned.
    """

    try:
        clients = get_kubernetes_clients()

        apps_v1 = clients["apps_v1"]

        if namespace:

            response = apps_v1.list_namespaced_deployment(
                namespace=namespace
            )

        else:

            response = (
                apps_v1
                .list_deployment_for_all_namespaces()
            )

        deployments = []

        for deployment in response.items:

            spec = deployment.spec
            status = deployment.status

            desired = (
                spec.replicas
                if spec
                else 0
            )

            ready = (
                status.ready_replicas or 0
                if status
                else 0
            )

            available = (
                status.available_replicas or 0
                if status
                else 0
            )

            deployments.append(
                {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                    "available_replicas": available,
                    "updated_replicas": (
                        status.updated_replicas or 0
                        if status
                        else 0
                    ),
                    "unavailable_replicas": (
                        status.unavailable_replicas or 0
                        if status
                        else 0
                    ),
                    "healthy": (
                        desired == ready
                        and desired == available
                    ),
                }
            )

        return {
            "success": True,
            "count": len(deployments),
            "deployments": deployments,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Replica Status
# ---------------------------------------------------------------------------


def get_deployment_replicas(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Get Deployment replica information.

    Useful for identifying:
    - desired replicas != ready replicas
    - unavailable replicas
    - failed rollouts
    """

    try:
        clients = get_kubernetes_clients()

        deployment = (
            clients["apps_v1"]
            .read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )
        )

        spec = deployment.spec
        status = deployment.status

        desired = (
            spec.replicas
            if spec
            else 0
        )

        ready = (
            status.ready_replicas or 0
            if status
            else 0
        )

        available = (
            status.available_replicas or 0
            if status
            else 0
        )

        updated = (
            status.updated_replicas or 0
            if status
            else 0
        )

        unavailable = (
            status.unavailable_replicas or 0
            if status
            else 0
        )

        return {
            "success": True,
            "namespace": namespace,
            "deployment": deployment_name,
            "replicas": {
                "desired": desired,
                "ready": ready,
                "available": available,
                "updated": updated,
                "unavailable": unavailable,
            },
            "healthy": (
                desired == ready
                and desired == available
            ),
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Deployment Conditions
# ---------------------------------------------------------------------------


def get_deployment_conditions(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Get Deployment conditions.

    Common conditions include:
    - Available
    - Progressing
    - ReplicaFailure
    """

    try:
        clients = get_kubernetes_clients()

        deployment = (
            clients["apps_v1"]
            .read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )
        )

        conditions = []

        for condition in deployment.status.conditions or []:

            conditions.append(
                {
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message,
                    "last_update_time": (
                        condition.last_update_time.isoformat()
                        if condition.last_update_time
                        else None
                    ),
                    "last_transition_time": (
                        condition.last_transition_time.isoformat()
                        if condition.last_transition_time
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "deployment": deployment_name,
            "conditions": conditions,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Rollout Status
# ---------------------------------------------------------------------------


def get_rollout_status(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Determine the current rollout status of a Deployment.

    This function does not perform kubectl rollout commands.
    It derives rollout status from the Kubernetes API.
    """

    try:
        clients = get_kubernetes_clients()

        deployment = (
            clients["apps_v1"]
            .read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )
        )

        spec = deployment.spec
        status = deployment.status

        desired = (
            spec.replicas
            if spec
            else 0
        )

        updated = (
            status.updated_replicas or 0
            if status
            else 0
        )

        ready = (
            status.ready_replicas or 0
            if status
            else 0
        )

        available = (
            status.available_replicas or 0
            if status
            else 0
        )

        generation = deployment.metadata.generation

        observed_generation = (
            status.observed_generation
            if status
            else None
        )

        progressing = False
        available_condition = False
        progress_message = None

        for condition in status.conditions or []:

            if condition.type == "Progressing":

                progressing = (
                    condition.status == "True"
                )

                progress_message = (
                    condition.message
                )

            elif condition.type == "Available":

                available_condition = (
                    condition.status == "True"
                )

        rollout_complete = (
            desired == updated
            and desired == ready
            and desired == available
            and observed_generation == generation
        )

        if rollout_complete:

            rollout_status = "Complete"

        elif progressing:

            rollout_status = "Progressing"

        else:

            rollout_status = "Stalled"

        return {
            "success": True,
            "namespace": namespace,
            "deployment": deployment_name,
            "rollout": {
                "status": rollout_status,
                "complete": rollout_complete,
                "desired_replicas": desired,
                "updated_replicas": updated,
                "ready_replicas": ready,
                "available_replicas": available,
                "observed_generation": observed_generation,
                "generation": generation,
                "progressing": progressing,
                "available": available_condition,
                "message": progress_message,
            },
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Deployment Problems
# ---------------------------------------------------------------------------


def detect_deployment_problems(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Detect common Deployment problems.

    This function identifies diagnostic signals.

    It does NOT determine the final root cause.
    The LangGraph diagnosis node will perform that reasoning.
    """

    try:
        clients = get_kubernetes_clients()

        deployment = (
            clients["apps_v1"]
            .read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )
        )

        spec = deployment.spec
        status = deployment.status

        problems: list[dict[str, Any]] = []

        desired = (
            spec.replicas
            if spec
            else 0
        )

        ready = (
            status.ready_replicas or 0
            if status
            else 0
        )

        available = (
            status.available_replicas or 0
            if status
            else 0
        )

        updated = (
            status.updated_replicas or 0
            if status
            else 0
        )

        unavailable = (
            status.unavailable_replicas or 0
            if status
            else 0
        )

        # ---------------------------------------------------------------
        # Replica mismatch
        # ---------------------------------------------------------------

        if desired != ready:

            problems.append(
                {
                    "type": "ReplicasNotReady",
                    "severity": "warning",
                    "message": (
                        f"Deployment requires {desired} replica(s), "
                        f"but only {ready} replica(s) are Ready."
                    ),
                    "desired": desired,
                    "ready": ready,
                }
            )

        # ---------------------------------------------------------------
        # Available replicas
        # ---------------------------------------------------------------

        if desired != available:

            problems.append(
                {
                    "type": "ReplicasUnavailable",
                    "severity": "warning",
                    "message": (
                        f"Deployment requires {desired} available "
                        f"replica(s), but only {available} are available."
                    ),
                    "desired": desired,
                    "available": available,
                }
            )

        # ---------------------------------------------------------------
        # Updated replicas
        # ---------------------------------------------------------------

        if desired != updated:

            problems.append(
                {
                    "type": "RolloutIncomplete",
                    "severity": "warning",
                    "message": (
                        f"Only {updated} of {desired} replica(s) "
                        "have been updated."
                    ),
                    "desired": desired,
                    "updated": updated,
                }
            )

        # ---------------------------------------------------------------
        # Unavailable replicas
        # ---------------------------------------------------------------

        if unavailable > 0:

            problems.append(
                {
                    "type": "UnavailableReplicas",
                    "severity": "critical",
                    "message": (
                        f"{unavailable} replica(s) are unavailable."
                    ),
                    "count": unavailable,
                }
            )

        # ---------------------------------------------------------------
        # Deployment conditions
        # ---------------------------------------------------------------

        for condition in status.conditions or []:

            # Progressing condition

            if (
                condition.type == "Progressing"
                and condition.status == "False"
            ):

                problems.append(
                    {
                        "type": "DeploymentProgressingFalse",
                        "severity": "critical",
                        "reason": condition.reason,
                        "message": condition.message,
                    }
                )

            # Available condition

            if (
                condition.type == "Available"
                and condition.status == "False"
            ):

                problems.append(
                    {
                        "type": "DeploymentUnavailable",
                        "severity": "critical",
                        "reason": condition.reason,
                        "message": condition.message,
                    }
                )

            # Replica failure

            if (
                condition.type == "ReplicaFailure"
                and condition.status == "True"
            ):

                problems.append(
                    {
                        "type": "ReplicaFailure",
                        "severity": "critical",
                        "reason": condition.reason,
                        "message": condition.message,
                    }
                )

        # ---------------------------------------------------------------
        # Observed generation
        # ---------------------------------------------------------------

        generation = deployment.metadata.generation

        observed_generation = (
            status.observed_generation
            if status
            else None
        )

        if (
            generation is not None
            and observed_generation is not None
            and generation != observed_generation
        ):

            problems.append(
                {
                    "type": "GenerationMismatch",
                    "severity": "warning",
                    "message": (
                        "Deployment controller has not yet observed "
                        "the latest Deployment generation."
                    ),
                    "generation": generation,
                    "observed_generation": observed_generation,
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "deployment": deployment_name,
            "problem_count": len(problems),
            "problems": problems,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Deployment Containers
# ---------------------------------------------------------------------------


def get_deployment_containers(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Get containers configured in the Deployment pod template.

    Secret values are never returned.

    Environment variable names are returned, but their values
    are intentionally excluded.
    """

    try:
        clients = get_kubernetes_clients()

        deployment = (
            clients["apps_v1"]
            .read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )
        )

        containers = []

        pod_spec = deployment.spec.template.spec

        if pod_spec:

            for container in pod_spec.containers or []:

                containers.append(
                    {
                        "name": container.name,
                        "image": container.image,
                        "image_pull_policy": (
                            container.image_pull_policy
                        ),
                        "ports": _serialize_ports(
                            container.ports
                        ),
                        "resources": _serialize_resources(
                            container.resources
                        ),
                        "environment_variables": (
                            _serialize_env_names(
                                container.env
                            )
                        ),
                    }
                )

        return {
            "success": True,
            "namespace": namespace,
            "deployment": deployment_name,
            "containers": containers,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# ReplicaSets
# ---------------------------------------------------------------------------


def get_deployment_replicasets(
    namespace: str,
    deployment_name: str,
) -> dict[str, Any]:
    """
    Find ReplicaSets associated with a Deployment.

    This is useful for diagnosing:
    - failed rollouts
    - old ReplicaSets
    - new ReplicaSet failures
    - rollout history problems
    """

    try:
        clients = get_kubernetes_clients()

        apps_v1 = clients["apps_v1"]

        deployment = apps_v1.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
        )

        selector = deployment.spec.selector.match_labels

        if not selector:

            return {
                "success": True,
                "namespace": namespace,
                "deployment": deployment_name,
                "replicasets": [],
                "message": (
                    "Deployment does not expose matchLabels "
                    "selector information."
                ),
            }

        label_selector = ",".join(
            f"{key}={value}"
            for key, value in selector.items()
        )

        replicasets = apps_v1.list_namespaced_replica_set(
            namespace=namespace,
            label_selector=label_selector,
        )

        results = []

        for replicaset in replicasets.items:

            owner_references = (
                replicaset.metadata.owner_references
                or []
            )

            owned_by_deployment = any(
                owner.kind == "Deployment"
                and owner.name == deployment_name
                for owner in owner_references
            )

            if not owned_by_deployment:
                continue

            status = replicaset.status
            spec = replicaset.spec

            results.append(
                {
                    "name": replicaset.metadata.name,
                    "namespace": replicaset.metadata.namespace,
                    "revision": (
                        replicaset.metadata.annotations.get(
                            "deployment.kubernetes.io/revision"
                        )
                        if replicaset.metadata.annotations
                        else None
                    ),
                    "desired_replicas": (
                        spec.replicas
                        if spec
                        else 0
                    ),
                    "ready_replicas": (
                        status.ready_replicas or 0
                        if status
                        else 0
                    ),
                    "available_replicas": (
                        status.available_replicas or 0
                        if status
                        else 0
                    ),
                    "fully_labeled_replicas": (
                        status.fully_labeled_replicas or 0
                        if status
                        else 0
                    ),
                }
            )

        return {
            "success": True,
            "namespace": namespace,
            "deployment": deployment_name,
            "count": len(results),
            "replicasets": results,
        }

    except ApiException as error:
        return _api_error(error)

    except Exception as error:
        return _unexpected_error(error)


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def _serialize_selector(
    selector: Any,
) -> dict[str, Any]:
    """
    Serialize Deployment selector.
    """

    if not selector:
        return {}

    return {
        "match_labels": selector.match_labels or {},
        "match_expressions": [
            {
                "key": expression.key,
                "operator": expression.operator,
                "values": expression.values or [],
            }
            for expression in (
                selector.match_expressions or []
            )
        ],
    }


def _serialize_strategy(
    strategy: Any,
) -> dict[str, Any]:
    """
    Serialize Deployment strategy.
    """

    if not strategy:
        return {}

    result = {
        "type": strategy.type,
    }

    if strategy.rolling_update:

        result["rolling_update"] = {
            "max_unavailable": (
                str(strategy.rolling_update.max_unavailable)
                if strategy.rolling_update.max_unavailable
                is not None
                else None
            ),
            "max_surge": (
                str(strategy.rolling_update.max_surge)
                if strategy.rolling_update.max_surge
                is not None
                else None
            ),
        }

    return result


def _serialize_resources(
    resources: Any,
) -> dict[str, Any]:
    """
    Serialize container resource requests and limits.
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


def _serialize_env_names(
    env_variables: Any,
) -> list[str]:
    """
    Return environment variable names only.

    Values are intentionally never returned.
    """

    if not env_variables:
        return []

    names = []

    for variable in env_variables:

        if variable.name:
            names.append(variable.name)

    return names


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
    Convert unexpected exceptions into safe dictionaries.
    """

    return {
        "success": False,
        "error": f"Unexpected error: {str(error)}",
    }