"""
Shared state definition for the AI Infrastructure Troubleshooting Agent.

The state is passed between LangGraph nodes during a troubleshooting
workflow.

Workflow:

    User Request
        ↓
    Analyze
        ↓
    Read Infrastructure
        ↓
    Diagnose
        ↓
    Recommend
"""

from typing import Any, TypedDict


class InfraState(TypedDict, total=False):
    """
    Shared state for the infrastructure troubleshooting workflow.
    """

    # ------------------------------------------------------------------
    # User Input
    # ------------------------------------------------------------------

    user_request: str

    # ------------------------------------------------------------------
    # Resource Identification
    # ------------------------------------------------------------------

    namespace: str | None

    resource: str | None

    resource_type: str | None

    resource_name: str | None

    # ------------------------------------------------------------------
    # Infrastructure Observations
    # ------------------------------------------------------------------

    observations: list[dict[str, Any]]

    # Kubernetes pod information
    pods: list[dict[str, Any]]

    # Kubernetes events
    events: list[dict[str, Any]]

    # Container/application logs
    logs: list[str]

    # Deployment information
    deployments: list[dict[str, Any]]

    # Service information
    services: list[dict[str, Any]]

    # Gateway / HTTPRoute information
    gateways: list[dict[str, Any]]

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    analysis: str | None

    symptoms: list[str]

    possible_causes: list[str]

    # ------------------------------------------------------------------
    # Diagnosis
    # ------------------------------------------------------------------

    diagnosis: str | None

    root_cause: str | None

    confidence: float

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    recommendations: list[str]

    recommended_commands: list[str]

    # ------------------------------------------------------------------
    # Execution / Verification
    # ------------------------------------------------------------------

    verification_required: bool

    verification_result: str | None

    # ------------------------------------------------------------------
    # Final Response
    # ------------------------------------------------------------------

    final_response: str | None

    # ------------------------------------------------------------------
    # Error Handling
    # ------------------------------------------------------------------

    error: str | None