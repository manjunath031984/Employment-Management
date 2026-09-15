"""
Tests for application entry point.
"""

from unittest.mock import patch

from app.main import (
    build_argument_parser,
    display_result,
    run_agent,
)


def test_argument_parser_request():

    parser = build_argument_parser()

    args = parser.parse_args(
        [
            "Why is my pod failing?"
        ]
    )

    assert (
        args.request
        == "Why is my pod failing?"
    )


def test_argument_parser_namespace():

    parser = build_argument_parser()

    args = parser.parse_args(
        [
            "Why is my pod failing?",
            "--namespace",
            "employment-management",
        ]
    )

    assert (
        args.namespace
        == "employment-management"
    )


def test_argument_parser_resource():

    parser = build_argument_parser()

    args = parser.parse_args(
        [
            "Why is my deployment unavailable?",
            "--namespace",
            "employment-management",
            "--resource-type",
            "deployment",
            "--resource-name",
            "employment-management",
        ]
    )

    assert (
        args.resource_type
        == "deployment"
    )

    assert (
        args.resource_name
        == "employment-management"
    )


def test_run_agent():

    result = run_agent(
        "Why is my pod in CrashLoopBackOff?"
    )

    assert result is not None

    assert (
        result["resource_type"]
        == "pod"
    )

    assert (
        "CrashLoopBackOff"
        in result["symptoms"]
    )


def test_run_agent_empty_request():

    try:

        run_agent("")

        assert False

    except ValueError as error:

        assert (
            "cannot be empty"
            in str(error)
        )


def test_display_result(capsys):

    result = {
        "user_request": (
            "Why is my pod failing?"
        ),
        "analysis": (
            "Detected pod resource."
        ),
        "resource_type": "pod",
        "resource_name": "test-pod",
        "namespace": "default",
        "symptoms": [
            "CrashLoopBackOff"
        ],
        "possible_causes": [
            "Application startup failure"
        ],
        "observations": [],
        "diagnosis": (
            "Pod is repeatedly failing."
        ),
        "root_cause": (
            "Application startup failure"
        ),
        "confidence": 0.65,
        "recommendations": [
            "Check pod logs."
        ],
        "recommended_commands": [
            "kubectl logs <pod>"
        ],
        "error": None,
    }

    display_result(result)

    captured = capsys.readouterr()

    assert (
        "AI INFRASTRUCTURE"
        in captured.out
    )

    assert (
        "CrashLoopBackOff"
        in captured.out
    )

    assert (
        "Application startup failure"
        in captured.out
    )


@patch(
    "app.main.infra_graph.invoke"
)
def test_run_agent_graph_failure(
    mock_invoke,
):

    mock_invoke.side_effect = (
        RuntimeError(
            "Graph failure"
        )
    )

    result = run_agent(
        "Test request"
    )

    assert (
        result["error"]
        == "Graph failure"
    )

    assert (
        "workflow failed"
        in result["final_response"]
    )