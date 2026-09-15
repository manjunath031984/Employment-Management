"""
Central Kubernetes client for the AI Infrastructure Troubleshooting Agent.

Responsibilities:
- Load Kubernetes configuration
- Support local kubeconfig
- Support in-cluster Kubernetes configuration
- Create Kubernetes API clients
- Reuse clients across the application
- Provide a single entry point for Kubernetes connectivity

Supported APIs:
- CoreV1Api
- AppsV1Api
- CustomObjectsApi
- NetworkingV1Api

IMPORTANT:
This module only creates Kubernetes API clients.

It does NOT:
- create resources
- update resources
- delete resources
- restart workloads
- scale workloads
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _get_kubeconfig_path() -> str | None:
    """
    Get the kubeconfig path from the environment.

    KUBECONFIG takes precedence.

    If KUBECONFIG is not set, the Kubernetes Python client will use
    the default kubeconfig location.
    """

    kubeconfig = os.getenv("KUBECONFIG")

    if kubeconfig:
        return kubeconfig

    return None


# ---------------------------------------------------------------------------
# Kubernetes Configuration Loading
# ---------------------------------------------------------------------------


def load_kubernetes_config() -> str:
    """
    Load Kubernetes configuration.

    Configuration order:

    1. In-cluster configuration
    2. Local kubeconfig

    This allows the same application to run:

    - locally on a developer machine
    - inside Docker
    - inside a Kubernetes Pod

    Returns:
        Configuration source used.
    """

    # ---------------------------------------------------------------
    # Try in-cluster configuration first
    # ---------------------------------------------------------------

    try:

        config.load_incluster_config()

        logger.info(
            "Kubernetes in-cluster configuration loaded."
        )

        return "in-cluster"

    except ConfigException:

        logger.debug(
            "In-cluster Kubernetes configuration "
            "not available."
        )

    # ---------------------------------------------------------------
    # Try local kubeconfig
    # ---------------------------------------------------------------

    kubeconfig_path = _get_kubeconfig_path()

    try:

        if kubeconfig_path:

            config.load_kube_config(
                config_file=kubeconfig_path
            )

            logger.info(
                "Kubernetes kubeconfig loaded from: %s",
                kubeconfig_path,
            )

        else:

            config.load_kube_config()

            logger.info(
                "Kubernetes default kubeconfig loaded."
            )

        return "kubeconfig"

    except ConfigException as error:

        raise RuntimeError(
            "Unable to load Kubernetes configuration. "
            "Make sure either in-cluster configuration is "
            "available or a valid kubeconfig exists."
        ) from error


# ---------------------------------------------------------------------------
# Kubernetes Clients
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_kubernetes_clients() -> dict[str, Any]:
    """
    Create and cache Kubernetes API clients.

    Returns:

        {
            "core_v1": CoreV1Api,
            "apps_v1": AppsV1Api,
            "custom_objects": CustomObjectsApi,
            "networking_v1": NetworkingV1Api,
        }

    The clients are cached so the application does not repeatedly
    reload kubeconfig or recreate API client objects.
    """

    source = load_kubernetes_config()

    logger.info(
        "Initializing Kubernetes API clients using %s configuration.",
        source,
    )

    return {
        "core_v1": client.CoreV1Api(),
        "apps_v1": client.AppsV1Api(),
        "custom_objects": client.CustomObjectsApi(),
        "networking_v1": client.NetworkingV1Api(),
    }


# ---------------------------------------------------------------------------
# Individual Client Accessors
# ---------------------------------------------------------------------------


def get_core_v1_client() -> client.CoreV1Api:
    """
    Return the Kubernetes CoreV1Api client.

    Handles:
    - Pods
    - Services
    - Endpoints
    - Namespaces
    - Events
    - ConfigMaps
    - Secrets
    - PVCs
    """

    clients = get_kubernetes_clients()

    return clients["core_v1"]


def get_apps_v1_client() -> client.AppsV1Api:
    """
    Return the Kubernetes AppsV1Api client.

    Handles:
    - Deployments
    - StatefulSets
    - ReplicaSets
    - DaemonSets
    """

    clients = get_kubernetes_clients()

    return clients["apps_v1"]


def get_custom_objects_client() -> client.CustomObjectsApi:
    """
    Return the Kubernetes CustomObjectsApi client.

    Used for:
    - Gateway
    - GatewayClass
    - HTTPRoute
    - Other CRDs
    """

    clients = get_kubernetes_clients()

    return clients["custom_objects"]


def get_networking_v1_client() -> client.NetworkingV1Api:
    """
    Return the Kubernetes NetworkingV1Api client.

    Used for standard Kubernetes networking resources such as:
    - Ingress
    - NetworkPolicy
    """

    clients = get_kubernetes_clients()

    return clients["networking_v1"]


# ---------------------------------------------------------------------------
# Connection Test
# ---------------------------------------------------------------------------


def test_kubernetes_connection() -> dict[str, Any]:
    """
    Test connectivity to the Kubernetes API server.

    This is READ-ONLY.

    It retrieves the Kubernetes API server version information.
    """

    try:

        clients = get_kubernetes_clients()

        version_api = client.VersionApi()

        version = version_api.get_code()

        return {
            "success": True,
            "message": (
                "Successfully connected to Kubernetes API."
            ),
            "version": {
                "major": version.major,
                "minor": version.minor,
                "git_version": version.git_version,
                "platform": version.platform,
                "go_version": version.go_version,
            },
        }

    except Exception as error:

        logger.exception(
            "Kubernetes connection test failed."
        )

        return {
            "success": False,
            "message": (
                "Unable to connect to Kubernetes API."
            ),
            "error": str(error),
        }


# ---------------------------------------------------------------------------
# Current Context
# ---------------------------------------------------------------------------


def get_current_kubernetes_context() -> dict[str, Any]:
    """
    Return the currently configured Kubernetes context.

    This is useful for troubleshooting the agent itself.

    Example:

        cluster: gke_student_management
        namespace: employment-management
    """

    try:

        contexts, active_context = (
            config.list_kube_config_contexts()
        )

        if not active_context:

            return {
                "success": False,
                "error": (
                    "No active Kubernetes context found."
                ),
            }

        context = active_context.get(
            "context",
            {},
        )

        return {
            "success": True,
            "context": {
                "name": active_context.get(
                    "name"
                ),
                "cluster": context.get(
                    "cluster"
                ),
                "user": context.get(
                    "user"
                ),
                "namespace": context.get(
                    "namespace",
                    "default",
                ),
            },
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error),
        }


# ---------------------------------------------------------------------------
# Namespace Helper
# ---------------------------------------------------------------------------


def get_current_namespace() -> str:
    """
    Get the namespace configured in the active kubeconfig context.

    If no namespace is configured, return 'default'.
    """

    try:

        contexts, active_context = (
            config.list_kube_config_contexts()
        )

        if not active_context:

            return "default"

        context = active_context.get(
            "context",
            {},
        )

        return context.get(
            "namespace",
            "default",
        ) or "default"

    except Exception:

        return "default"


# ---------------------------------------------------------------------------
# Cache Management
# ---------------------------------------------------------------------------


def reset_kubernetes_clients() -> None:
    """
    Clear cached Kubernetes clients.

    Useful when:
    - kubeconfig changes
    - active context changes
    - credentials are refreshed
    - tests need a clean client state
    """

    get_kubernetes_clients.cache_clear()

    logger.info(
        "Kubernetes client cache cleared."
    )