"""
LangGraph workflow for the AI Infrastructure Troubleshooting Agent.

This module defines the troubleshooting workflow and compiles
the LangGraph state machine.

Workflow:

    START
      |
      v
   ANALYZE
      |
      v
     READ
      |
      v
   DIAGNOSE
      |
      v
  RECOMMEND
      |
      v
     END

Responsibilities:

- graph.py  -> workflow orchestration
- state.py  -> shared state
- nodes.py  -> node/business logic
- prompts.py -> LLM prompt templates
"""

from langgraph.graph import END, START, StateGraph

from app.agent.nodes import (
    analyze_problem,
    diagnose_problem,
    generate_recommendation,
    read_infrastructure,
)
from app.agent.state import InfraState


# ============================================================================
# GRAPH BUILDER
# ============================================================================

def build_graph():
    """
    Build and compile the AI Infrastructure Troubleshooting graph.

    The graph follows a controlled READ -> ANALYZE -> DIAGNOSE ->
    RECOMMEND workflow.

    Returns:
        Compiled LangGraph workflow.
    """

    # ------------------------------------------------------------------------
    # Create StateGraph using the shared InfraState
    # ------------------------------------------------------------------------

    builder = StateGraph(InfraState)

    # ------------------------------------------------------------------------
    # Register Nodes
    # ------------------------------------------------------------------------

    builder.add_node(
        "analyze",
        analyze_problem,
    )

    builder.add_node(
        "read",
        read_infrastructure,
    )

    builder.add_node(
        "diagnose",
        diagnose_problem,
    )

    builder.add_node(
        "recommend",
        generate_recommendation,
    )

    # ------------------------------------------------------------------------
    # Define Workflow
    # ------------------------------------------------------------------------

    builder.add_edge(
        START,
        "analyze",
    )

    builder.add_edge(
        "analyze",
        "read",
    )

    builder.add_edge(
        "read",
        "diagnose",
    )

    builder.add_edge(
        "diagnose",
        "recommend",
    )

    builder.add_edge(
        "recommend",
        END,
    )

    # ------------------------------------------------------------------------
    # Compile Graph
    # ------------------------------------------------------------------------

    return builder.compile()


# ============================================================================
# COMPILED GRAPH
# ============================================================================

infra_graph = build_graph()