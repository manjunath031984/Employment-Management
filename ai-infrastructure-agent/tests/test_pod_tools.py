"""
Tests for Pod troubleshooting tools.
"""

from app.tools.pod_tools import (
    check_pod_readiness,
    detect_pod_problems,
    get_container_status,
    get_pod_logs,
    inspect_pod,
    list_pods,
)


def test_inspect_pod(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = (
        make_pod()
    )

    result = inspect_pod(
        "default",
        "test-pod",
    )

    assert result["success"] is True

    assert (
        result["pod"]["name"]
        == "test-pod"
    )

    assert (
        result["pod"]["phase"]
        == "Running"
    )

    assert (
        result["pod"]["container_statuses"]
    )


def test_list_pods(
    mock_clients,
):

    from tests.conftest import make_pod

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

    result = list_pods(
        "default"
    )

    assert result["success"] is True

    assert result["count"] == 2


def test_get_pod_logs_current(
    mock_clients,
):

    mock_clients[
        "core_v1"
    ].read_namespaced_pod_log.return_value = (
        "Application started successfully"
    )

    result = get_pod_logs(
        namespace="default",
        pod_name="test-pod",
        tail_lines=100,
    )

    assert result["success"] is True

    assert (
        "Application started"
        in result["logs"]
    )

    assert result["previous"] is False


def test_get_previous_pod_logs(
    mock_clients,
):

    mock_clients[
        "core_v1"
    ].read_namespaced_pod_log.return_value = (
        "Previous container crashed"
    )

    result = get_pod_logs(
        namespace="default",
        pod_name="test-pod",
        previous=True,
    )

    assert result["success"] is True

    assert result["previous"] is True

    mock_clients[
        "core_v1"
    ].read_namespaced_pod_log.assert_called_once()


def test_detect_crashloop(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = make_pod(
        ready=False,
        restart_count=5,
        container_state="waiting",
    )

    result = detect_pod_problems(
        "default",
        "test-pod",
    )

    assert result["success"] is True

    problem_types = [
        problem["type"]
        for problem in result["problems"]
    ]

    assert (
        "CrashLoopBackOff"
        in problem_types
    )


def test_detect_oomkilled(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = make_pod(
        ready=False,
        container_state="oom",
    )

    result = detect_pod_problems(
        "default",
        "test-pod",
    )

    problem_types = [
        problem["type"]
        for problem in result["problems"]
    ]

    assert "OOMKilled" in problem_types


def test_detect_restart_problem(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = make_pod(
        restart_count=10,
    )

    result = detect_pod_problems(
        "default",
        "test-pod",
    )

    problem_types = [
        problem["type"]
        for problem in result["problems"]
    ]

    assert (
        "ContainerRestarts"
        in problem_types
    )


def test_container_status(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = (
        make_pod()
    )

    result = get_container_status(
        "default",
        "test-pod",
    )

    assert result["success"] is True

    assert len(
        result["containers"]
    ) == 1

    assert (
        result["containers"][0]["name"]
        == "app"
    )


def test_pod_readiness_true(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = (
        make_pod(
            ready=True
        )
    )

    result = check_pod_readiness(
        "default",
        "test-pod",
    )

    assert result["success"] is True

    assert result["ready"] is True


def test_pod_readiness_false(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = (
        make_pod(
            ready=False
        )
    )

    result = check_pod_readiness(
        "default",
        "test-pod",
    )

    assert result["success"] is True

    assert result["ready"] is False


def test_log_limit(
    mock_clients,
):

    mock_clients[
        "core_v1"
    ].read_namespaced_pod_log.return_value = (
        "logs"
    )

    get_pod_logs(
        namespace="default",
        pod_name="test-pod",
        tail_lines=5000,
    )

    call = (
        mock_clients[
            "core_v1"
        ].read_namespaced_pod_log.call_args
    )

    assert (
        call.kwargs["tail_lines"]
        == 1000
    )


def test_secret_value_is_not_exposed(
    mock_clients,
):

    from tests.conftest import make_pod

    mock_clients[
        "core_v1"
    ].read_namespaced_pod.return_value = (
        make_pod()
    )

    result = inspect_pod(
        "default",
        "test-pod",
    )

    result_string = str(result)

    assert (
        "SECRET_VALUE"
        not in result_string
    )