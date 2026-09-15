"""
Tests for InfraState.
"""

from app.agent.state import InfraState


def test_infra_state_accepts_basic_values():
    state: InfraState = {
        "user_request": "Why is my pod failing?",
        "namespace": "default",
        "resource_type": "pod",
        "resource_name": "test-pod",
        "symptoms": ["CrashLoopBackOff"],
        "possible_causes": [
            "Application startup failure"
        ],
        "confidence": 0.65,
    }

    assert state["user_request"] == (
        "Why is my pod failing?"
    )

    assert state["namespace"] == "default"

    assert state["resource_type"] == "pod"

    assert state["confidence"] == 0.65


def test_infra_state_is_partial():
    state: InfraState = {
        "user_request": "Test request"
    }

    assert state["user_request"] == "Test request"


def test_infra_state_supports_observations():
    state: InfraState = {
        "observations": [
            {
                "resource": "pod",
                "status": "Running",
            }
        ]
    }

    assert len(state["observations"]) == 1