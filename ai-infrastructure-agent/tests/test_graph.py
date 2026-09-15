"""
Tests for LangGraph workflow.
"""

from app.agent.graph import build_graph, infra_graph


def test_graph_is_compiled():

    graph = build_graph()

    assert graph is not None


def test_graph_contains_expected_nodes():

    graph = build_graph()

    nodes = graph.nodes

    assert "analyze" in nodes

    assert "read" in nodes

    assert "diagnose" in nodes

    assert "recommend" in nodes


def test_graph_executes():

    result = infra_graph.invoke(
        {
            "user_request": (
                "Why is my pod in CrashLoopBackOff?"
            )
        }
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

    assert result["diagnosis"]

    assert result["recommendations"]