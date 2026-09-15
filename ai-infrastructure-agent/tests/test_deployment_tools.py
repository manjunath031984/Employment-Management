"""
Tests for Deployment troubleshooting tools.
"""

from app.tools.deployment_tools import (
    detect_deployment_problems,
    get_deployment_conditions,
    get_deployment_containers,
    get_deployment_replicas,
    get_deployment_replicasets,
    get_rollout_status,
    inspect_deployment,
    list_deployments,
)


def test_inspect_deployment(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment()
    )

    result = inspect_deployment(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert (
        result["deployment"]["name"]
        == "test-deployment"
    )

    assert (
        result["deployment"]["replicas"]
        == 2
    )


def test_list_deployments(
    mock_clients,
):

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

    result = list_deployments(
        "default"
    )

    assert result["success"] is True

    assert result["count"] == 1

    assert (
        result["deployments"][0]["healthy"]
        is True
    )


def test_get_deployment_replicas(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment(
            desired=3,
            ready=2,
            available=2,
            updated=3,
            unavailable=1,
        )
    )

    result = get_deployment_replicas(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert (
        result["replicas"]["desired"]
        == 3
    )

    assert (
        result["replicas"]["ready"]
        == 2
    )

    assert result["healthy"] is False


def test_get_rollout_status_complete(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment()
    )

    result = get_rollout_status(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert (
        result["rollout"]["status"]
        == "Complete"
    )

    assert (
        result["rollout"]["complete"]
        is True
    )


def test_get_rollout_status_progressing(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment(
            desired=3,
            ready=1,
            available=1,
            updated=2,
            unavailable=2,
        )
    )

    result = get_rollout_status(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert (
        result["rollout"]["status"]
        in {
            "Progressing",
            "Stalled",
        }
    )


def test_get_deployment_conditions(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment()
    )

    result = get_deployment_conditions(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert len(
        result["conditions"]
    ) == 2


def test_detect_deployment_problems(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment(
            desired=3,
            ready=1,
            available=1,
            updated=2,
            unavailable=2,
        )
    )

    result = detect_deployment_problems(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    problem_types = [
        problem["type"]
        for problem in result["problems"]
    ]

    assert (
        "ReplicasNotReady"
        in problem_types
    )

    assert (
        "ReplicasUnavailable"
        in problem_types
    )


def test_get_deployment_containers(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment()
    )

    result = get_deployment_containers(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert len(
        result["containers"]
    ) == 1

    assert (
        result["containers"][0]["image"]
        == "nginx:latest"
    )


def test_deployment_does_not_expose_secret_values(
    mock_clients,
):

    from tests.conftest import make_deployment

    deployment = make_deployment()

    deployment.spec.template.spec.containers[
        0
    ].env.append(
        type(
            "Env",
            (),
            {
                "name": "PASSWORD",
                "value": "SUPER_SECRET",
            },
        )()
    )

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        deployment
    )

    result = get_deployment_containers(
        "default",
        "test-deployment",
    )

    assert (
        "SUPER_SECRET"
        not in str(result)
    )


def test_get_deployment_replicasets(
    mock_clients,
):

    from tests.conftest import make_deployment

    mock_clients[
        "apps_v1"
    ].read_namespaced_deployment.return_value = (
        make_deployment()
    )

    replicaset = type(
        "ReplicaSet",
        (),
        {
            "metadata": type(
                "Metadata",
                (),
                {
                    "name": "test-deployment-123",
                    "namespace": "default",
                    "annotations": {
                        "deployment.kubernetes.io/revision": "1"
                    },
                    "owner_references": [
                        type(
                            "Owner",
                            (),
                            {
                                "kind": "Deployment",
                                "name": "test-deployment",
                            },
                        )()
                    ],
                },
            )(),
            "spec": type(
                "Spec",
                (),
                {
                    "replicas": 2,
                },
            )(),
            "status": type(
                "Status",
                (),
                {
                    "ready_replicas": 2,
                    "available_replicas": 2,
                    "fully_labeled_replicas": 2,
                },
            )(),
        },
    )()

    mock_clients[
        "apps_v1"
    ].list_namespaced_replica_set.return_value = type(
        "Response",
        (),
        {
            "items": [
                replicaset
            ]
        },
    )()

    result = get_deployment_replicasets(
        "default",
        "test-deployment",
    )

    assert result["success"] is True

    assert result["count"] == 1