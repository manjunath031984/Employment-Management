"""
Tests for LangGraph nodes.
"""

from app.agent.nodes import (
    analyze_problem,
    diagnose_problem,
    generate_recommendation,
    read_infrastructure,
)


# ---------------------------------------------------------------------------
# Analyze
# ---------------------------------------------------------------------------


def test_analyze_empty_request():

    result = analyze_problem(
        {
            "user_request": ""
        }
    )

    assert "error" in result

    assert (
        result["error"]
        == "No infrastructure troubleshooting request was provided."
    )


def test_analyze_pod_crashloop():

    result = analyze_problem(
        {
            "user_request": (
                "Why is my pod in CrashLoopBackOff?"
            )
        }
    )

    assert result["resource_type"] == "pod"

    assert "CrashLoopBackOff" in result["symptoms"]

    assert len(
        result["possible_causes"]
    ) > 0


def test_analyze_oomkilled():

    result = analyze_problem(
        {
            "user_request": (
                "My pod was OOMKilled"
            )
        }
    )

    assert "OOMKilled" in result["symptoms"]

    assert (
        "Container memory limit is too low"
        in result["possible_causes"]
    )


def test_analyze_pending():

    result = analyze_problem(
        {
            "user_request": (
                "Why is my pod Pending?"
            )
        }
    )

    assert "Pending" in result["symptoms"]

    assert (
        "Insufficient cluster resources"
        in result["possible_causes"]
    )


def test_analyze_image_pull_error():

    result = analyze_problem(
        {
            "user_request": (
                "Pod has ImagePullBackOff"
            )
        }
    )

    assert (
        "ImagePullBackOff"
        in result["symptoms"]
    )


def test_analyze_service_connection_refused():

    result = analyze_problem(
        {
            "user_request": (
                "Service connection refused"
            )
        }
    )

    assert result["resource_type"] == "service"

    assert (
        "connection refused"
        in result["symptoms"]
    )


# ---------------------------------------------------------------------------
# Read Infrastructure
# ---------------------------------------------------------------------------


def test_read_infrastructure_is_read_only():

    result = read_infrastructure(
        {
            "resource_type": "pod",
            "resource_name": "test-pod",
            "namespace": "default",
        }
    )

    assert result["observations"]

    assert result["pods"] == []

    assert result["deployments"] == []

    assert result["services"] == []

    assert result["gateways"] == []


# ---------------------------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------------------------


def test_diagnose_crashloop():

    result = diagnose_problem(
        {
            "symptoms": [
                "CrashLoopBackOff"
            ],
            "possible_causes": [
                "Application startup failure"
            ],
            "observations": [],
        }
    )

    assert (
        result["root_cause"]
        == (
            "The workload is repeatedly failing and "
            "Kubernetes is restarting the container."
        )
    )

    assert result["confidence"] == 0.65


def test_diagnose_oom():

    result = diagnose_problem(
        {
            "symptoms": [
                "OOMKilled"
            ],
            "possible_causes": [],
            "observations": [],
        }
    )

    assert (
        result["root_cause"]
        == "The container exceeded its available memory limit."
    )

    assert result["confidence"] == 0.85


def test_diagnose_pending():

    result = diagnose_problem(
        {
            "symptoms": [
                "Pending"
            ],
            "possible_causes": [],
            "observations": [],
        }
    )

    assert (
        "cannot currently be scheduled"
        in result["root_cause"]
    )

    assert result["confidence"] == 0.70


def test_diagnose_image_pull():

    result = diagnose_problem(
        {
            "symptoms": [
                "ImagePullBackOff"
            ],
            "possible_causes": [],
            "observations": [],
        }
    )

    assert (
        "unable to pull"
        in result["root_cause"]
    )


def test_diagnose_connection_refused():

    result = diagnose_problem(
        {
            "symptoms": [
                "connection refused"
            ],
            "possible_causes": [],
            "observations": [],
        }
    )

    assert (
        "connection"
        in result["root_cause"]
    )


def test_diagnose_unknown():

    result = diagnose_problem(
        {
            "symptoms": [],
            "possible_causes": [
                "Configuration issue"
            ],
            "observations": [],
        }
    )

    assert result["confidence"] == 0.30


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------


def test_recommendation_crashloop():

    result = generate_recommendation(
        {
            "symptoms": [
                "CrashLoopBackOff"
            ],
            "root_cause": "Container failure",
        }
    )

    assert result["recommendations"]

    assert any(
        "logs"
        in recommendation.lower()
        for recommendation in result[
            "recommendations"
        ]
    )

    assert result["recommended_commands"]

    assert result["verification_required"] is True


def test_recommendation_oom():

    result = generate_recommendation(
        {
            "symptoms": [
                "OOMKilled"
            ],
            "root_cause": "Memory limit exceeded",
        }
    )

    assert any(
        "memory"
        in recommendation.lower()
        for recommendation in result[
            "recommendations"
        ]
    )


def test_recommendation_pending():

    result = generate_recommendation(
        {
            "symptoms": [
                "Pending"
            ],
            "root_cause": "Scheduling issue",
        }
    )

    assert any(
        "node"
        in recommendation.lower()
        for recommendation in result[
            "recommendations"
        ]
    )


def test_recommendation_image_pull():

    result = generate_recommendation(
        {
            "symptoms": [
                "ImagePullBackOff"
            ],
            "root_cause": "Image unavailable",
        }
    )

    assert any(
        "image"
        in recommendation.lower()
        for recommendation in result[
            "recommendations"
        ]
    )


def test_recommendation_connection_refused():

    result = generate_recommendation(
        {
            "symptoms": [
                "connection refused"
            ],
            "root_cause": "Service connectivity issue",
        }
    )

    assert any(
        "service"
        in recommendation.lower()
        for recommendation in result[
            "recommendations"
        ]
    )


def test_recommendation_unknown():

    result = generate_recommendation(
        {
            "symptoms": [],
            "root_cause": None,
        }
    )

    assert result["recommendations"]

    assert result["recommended_commands"]

    assert result["verification_required"] is True