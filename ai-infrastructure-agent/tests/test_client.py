"""
Tests for Kubernetes client configuration.
"""

from unittest.mock import MagicMock

import pytest

from kubernetes.config.config_exception import ConfigException

import app.kubernetes.client as kubernetes_client


def test_load_incluster_config(monkeypatch):

    load_incluster = MagicMock()

    load_kubeconfig = MagicMock()

    monkeypatch.setattr(
        kubernetes_client.config,
        "load_incluster_config",
        load_incluster,
    )

    monkeypatch.setattr(
        kubernetes_client.config,
        "load_kube_config",
        load_kubeconfig,
    )

    result = (
        kubernetes_client
        .load_kubernetes_config()
    )

    assert result == "in-cluster"

    load_incluster.assert_called_once()

    load_kubeconfig.assert_not_called()


def test_load_local_kubeconfig(monkeypatch):

    def fail_incluster():

        raise ConfigException(
            "Not running in cluster"
        )

    load_kubeconfig = MagicMock()

    monkeypatch.setattr(
        kubernetes_client.config,
        "load_incluster_config",
        fail_incluster,
    )

    monkeypatch.setattr(
        kubernetes_client.config,
        "load_kube_config",
        load_kubeconfig,
    )

    result = (
        kubernetes_client
        .load_kubernetes_config()
    )

    assert result == "kubeconfig"

    load_kubeconfig.assert_called_once()


def test_kubeconfig_environment_variable(
    monkeypatch,
):

    monkeypatch.setenv(
        "KUBECONFIG",
        "C:/test/config",
    )

    assert (
        kubernetes_client
        ._get_kubeconfig_path()
        == "C:/test/config"
    )


def test_kubeconfig_default(
    monkeypatch,
):

    monkeypatch.delenv(
        "KUBECONFIG",
        raising=False,
    )

    assert (
        kubernetes_client
        ._get_kubeconfig_path()
        is None
    )


def test_get_kubernetes_clients(
    monkeypatch,
):

    monkeypatch.setattr(
        kubernetes_client,
        "load_kubernetes_config",
        lambda: "kubeconfig",
    )

    clients = (
        kubernetes_client
        .get_kubernetes_clients()
    )

    assert "core_v1" in clients

    assert "apps_v1" in clients

    assert "custom_objects" in clients

    assert "networking_v1" in clients

    kubernetes_client.get_kubernetes_clients.cache_clear()


def test_test_kubernetes_connection(monkeypatch):

    fake_version = MagicMock()

    fake_version.major = "1"

    fake_version.minor = "33"

    fake_version.git_version = "v1.33.0"

    fake_version.platform = "linux/amd64"

    fake_version.go_version = "go1.24"

    version_api = MagicMock()

    version_api.get_code.return_value = (
        fake_version
    )

    monkeypatch.setattr(
        kubernetes_client.client,
        "VersionApi",
        lambda: version_api,
    )

    fake_clients = {
        "core_v1": MagicMock(),
        "apps_v1": MagicMock(),
        "custom_objects": MagicMock(),
        "networking_v1": MagicMock(),
    }

    monkeypatch.setattr(
        kubernetes_client,
        "get_kubernetes_clients",
        lambda: fake_clients,
    )

    result = (
        kubernetes_client
        .test_kubernetes_connection()
    )

    assert result["success"] is True

    assert (
        result["version"]["git_version"]
        == "v1.33.0"
    )


def test_current_namespace(
    monkeypatch,
):

    monkeypatch.setattr(
        kubernetes_client.config,
        "list_kube_config_contexts",
        lambda: (
            [],
            {
                "name": "test-context",
                "context": {
                    "namespace": "employment-management"
                },
            },
        ),
    )

    assert (
        kubernetes_client
        .get_current_namespace()
        == "employment-management"
    )


def test_current_namespace_defaults(
    monkeypatch,
):

    monkeypatch.setattr(
        kubernetes_client.config,
        "list_kube_config_contexts",
        lambda: (
            [],
            {
                "name": "test-context",
                "context": {},
            },
        ),
    )

    assert (
        kubernetes_client
        .get_current_namespace()
        == "default"
    )