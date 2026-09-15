"""
LangGraph nodes for the AI Infrastructure Troubleshooting Agent.

The nodes are responsible for processing and updating InfraState.

Workflow:

    ANALYZE
       ↓
    READ INFRASTRUCTURE
       ↓
    DIAGNOSE
       ↓
    RECOMMEND
"""

from typing import Any

from app.agent.state import InfraState


# ============================================================================
# ANALYZE NODE
# ============================================================================

def analyze_problem(state: InfraState) -> dict[str, Any]:
    """
    Analyze the user's infrastructure troubleshooting request.

    This node identifies:
    - Resource type
    - Resource name
    - Namespace
    - Symptoms
    - Possible causes

    LLM-based analysis will be added in a later phase.
    """

    user_request = state.get("user_request", "").strip()

    if not user_request:
        return {
            "error": "No infrastructure troubleshooting request was provided."
        }

    request_lower = user_request.lower()

    # ------------------------------------------------------------------------
    # Detect Kubernetes resource type
    # ------------------------------------------------------------------------

    resource_type: str | None = None

    resource_keywords = {
        "pod": ["pod", "pods"],
        "deployment": ["deployment", "deployments"],
        "service": ["service", "services", "svc"],
        "gateway": ["gateway", "gateways"],
        "httproute": ["httproute", "http route", "http-route"],
        "statefulset": ["statefulset", "stateful set"],
        "pvc": ["pvc", "persistent volume claim"],
    }

    for resource, keywords in resource_keywords.items():
        if any(keyword in request_lower for keyword in keywords):
            resource_type = resource
            break

    # ------------------------------------------------------------------------
    # Detect common Kubernetes symptoms
    # ------------------------------------------------------------------------

    symptoms: list[str] = []

    symptom_keywords = {
        "CrashLoopBackOff": [
            "crashloopbackoff",
            "crash loop",
            "crashing",
        ],
        "OOMKilled": [
            "oomkilled",
            "out of memory",
            "memory exceeded",
        ],
        "Pending": [
            "pending",
            "pod pending",
        ],
        "ImagePullBackOff": [
            "imagepullbackoff",
            "image pull",
            "image cannot be pulled",
        ],
        "ErrImagePull": [
            "errimagepull",
            "image pull error",
        ],
        "connection refused": [
            "connection refused",
            "connection refused error",
        ],
        "timeout": [
            "timeout",
            "timed out",
        ],
        "not ready": [
            "not ready",
            "readiness",
            "readiness probe",
        ],
        "liveness failure": [
            "liveness",
            "liveness probe",
        ],
    }

    for symptom, keywords in symptom_keywords.items():
        if any(keyword in request_lower for keyword in keywords):
            symptoms.append(symptom)

    # ------------------------------------------------------------------------
    # Determine possible causes
    # ------------------------------------------------------------------------

    possible_causes: list[str] = []

    if "CrashLoopBackOff" in symptoms:
        possible_causes.extend(
            [
                "Application startup failure",
                "Configuration error",
                "Missing environment variables",
                "Database connectivity failure",
                "Application dependency failure",
            ]
        )

    if "OOMKilled" in symptoms:
        possible_causes.extend(
            [
                "Container memory limit is too low",
                "Application memory consumption is too high",
                "Memory leak",
            ]
        )

    if "Pending" in symptoms:
        possible_causes.extend(
            [
                "Insufficient cluster resources",
                "Node scheduling constraints",
                "Pod affinity or anti-affinity",
                "Node taints and tolerations",
                "PersistentVolumeClaim unavailable",
            ]
        )

    if "ImagePullBackOff" in symptoms or "ErrImagePull" in symptoms:
        possible_causes.extend(
            [
                "Container image does not exist",
                "Incorrect image tag",
                "Container registry authentication failure",
                "Registry connectivity issue",
            ]
        )

    if "connection refused" in symptoms:
        possible_causes.extend(
            [
                "Target service is unavailable",
                "Incorrect service name or port",
                "Backend pod is not ready",
                "Network connectivity problem",
            ]
        )

    if not possible_causes:
        possible_causes.extend(
            [
                "Application configuration issue",
                "Kubernetes resource configuration issue",
                "Dependency availability issue",
                "Networking issue",
            ]
        )

    # Remove duplicate causes while preserving order
    possible_causes = list(dict.fromkeys(possible_causes))

    analysis = (
        f"Analyzing infrastructure request: '{user_request}'. "
        f"Detected resource type: {resource_type or 'unknown'}. "
        f"Detected symptoms: {symptoms or ['none explicitly detected']}."
    )

    return {
        "analysis": analysis,
        "resource_type": resource_type,
        "symptoms": symptoms,
        "possible_causes": possible_causes,
        "error": None,
    }


# ============================================================================
# READ INFRASTRUCTURE NODE
# ============================================================================

def read_infrastructure(state: InfraState) -> dict[str, Any]:
    """
    Collect infrastructure observations.

    Kubernetes tool integration will be connected here.

    IMPORTANT:
    This node currently does not execute kubectl commands or modify
    Kubernetes resources.

    It is READ-ONLY.
    """

    resource_type = state.get("resource_type")
    namespace = state.get("namespace")
    resource_name = state.get("resource_name")

    observations: list[dict[str, Any]] = []

    # ------------------------------------------------------------------------
    # Current phase:
    # Do not call Kubernetes yet.
    # ------------------------------------------------------------------------

    observations.append(
        {
            "status": "pending",
            "resource_type": resource_type,
            "resource_name": resource_name,
            "namespace": namespace,
            "message": (
                "Kubernetes read-only tools will be connected "
                "in the Kubernetes integration phase."
            ),
        }
    )

    return {
        "observations": observations,
        "pods": [],
        "events": [],
        "logs": [],
        "deployments": [],
        "services": [],
        "gateways": [],
        "error": None,
    }


# ============================================================================
# DIAGNOSE NODE
# ============================================================================

def diagnose_problem(state: InfraState) -> dict[str, Any]:
    """
    Diagnose the infrastructure problem using collected observations.

    LLM-based reasoning will be added through LangChain in a later phase.

    The current implementation performs deterministic diagnosis based
    on detected symptoms.
    """

    symptoms = state.get("symptoms", [])
    possible_causes = state.get("possible_causes", [])
    observations = state.get("observations", [])

    diagnosis = "Unable to determine the root cause with the available evidence."

    root_cause: str | None = None
    confidence = 0.0

    # ------------------------------------------------------------------------
    # Deterministic diagnosis
    # ------------------------------------------------------------------------

    if "CrashLoopBackOff" in symptoms:
        root_cause = (
            "The workload is repeatedly failing and Kubernetes is restarting "
            "the container."
        )

        diagnosis = (
            "The pod appears to be experiencing a CrashLoopBackOff condition. "
            "Application logs and Kubernetes events are required to determine "
            "the exact root cause."
        )

        confidence = 0.65

    elif "OOMKilled" in symptoms:
        root_cause = "The container exceeded its available memory limit."

        diagnosis = (
            "The container appears to have been terminated because it exceeded "
            "its configured memory limit."
        )

        confidence = 0.85

    elif "Pending" in symptoms:
        root_cause = (
            "The pod cannot currently be scheduled on an available node."
        )

        diagnosis = (
            "The pod is in Pending state. Kubernetes scheduling information, "
            "node resources, taints, tolerations, and events should be checked."
        )

        confidence = 0.70

    elif (
        "ImagePullBackOff" in symptoms
        or "ErrImagePull" in symptoms
    ):
        root_cause = "Kubernetes is unable to pull the requested container image."

        diagnosis = (
            "The workload cannot start because the container image could not "
            "be retrieved from the configured registry."
        )

        confidence = 0.85

    elif "connection refused" in symptoms:
        root_cause = (
            "The application cannot establish a connection to the target "
            "service."
        )

        diagnosis = (
            "A backend connection is being refused. The target service, "
            "endpoint, port, and backend pod health should be investigated."
        )

        confidence = 0.75

    else:
        if possible_causes:
            root_cause = possible_causes[0]

        diagnosis = (
            "The available information is insufficient to determine a "
            "high-confidence root cause."
        )

        confidence = 0.30

    return {
        "diagnosis": diagnosis,
        "root_cause": root_cause,
        "confidence": confidence,
        "error": None,
    }


# ============================================================================
# RECOMMENDATION NODE
# ============================================================================

def generate_recommendation(state: InfraState) -> dict[str, Any]:
    """
    Generate troubleshooting recommendations.

    This node is currently rule-based.

    LangChain/OpenAI-based recommendations will be introduced in a later
    implementation phase.
    """

    symptoms = state.get("symptoms", [])
    root_cause = state.get("root_cause")

    recommendations: list[str] = []
    recommended_commands: list[str] = []

    # ------------------------------------------------------------------------
    # CrashLoopBackOff
    # ------------------------------------------------------------------------

    if "CrashLoopBackOff" in symptoms:
        recommendations.extend(
            [
                "Check the pod logs.",
                "Check the pod events.",
                "Check container exit codes.",
                "Verify application configuration.",
                "Verify required environment variables.",
                "Verify database and external service connectivity.",
            ]
        )

        recommended_commands.extend(
            [
                "kubectl logs <pod> -n <namespace>",
                "kubectl describe pod <pod> -n <namespace>",
                "kubectl get events -n <namespace>",
            ]
        )

    # ------------------------------------------------------------------------
    # OOMKilled
    # ------------------------------------------------------------------------

    if "OOMKilled" in symptoms:
        recommendations.extend(
            [
                "Check the container memory limit.",
                "Review application memory usage.",
                "Check for possible memory leaks.",
                "Review historical memory utilization.",
            ]
        )

        recommended_commands.extend(
            [
                "kubectl describe pod <pod> -n <namespace>",
                "kubectl top pod <pod> -n <namespace>",
            ]
        )

    # ------------------------------------------------------------------------
    # Pending
    # ------------------------------------------------------------------------

    if "Pending" in symptoms:
        recommendations.extend(
            [
                "Check pod scheduling events.",
                "Check available node CPU and memory.",
                "Check node taints and pod tolerations.",
                "Check PersistentVolumeClaim status.",
            ]
        )

        recommended_commands.extend(
            [
                "kubectl describe pod <pod> -n <namespace>",
                "kubectl get nodes",
                "kubectl describe nodes",
            ]
        )

    # ------------------------------------------------------------------------
    # Image pull problems
    # ------------------------------------------------------------------------

    if (
        "ImagePullBackOff" in symptoms
        or "ErrImagePull" in symptoms
    ):
        recommendations.extend(
            [
                "Verify the container image name.",
                "Verify the image tag.",
                "Verify registry authentication.",
                "Verify that the image exists in the registry.",
            ]
        )

        recommended_commands.extend(
            [
                "kubectl describe pod <pod> -n <namespace>",
            ]
        )

    # ------------------------------------------------------------------------
    # Connection problems
    # ------------------------------------------------------------------------

    if "connection refused" in symptoms:
        recommendations.extend(
            [
                "Verify that the target service exists.",
                "Verify the service port and targetPort.",
                "Check backend pod readiness.",
                "Check service endpoints.",
                "Verify application configuration.",
            ]
        )

        recommended_commands.extend(
            [
                "kubectl get service -n <namespace>",
                "kubectl describe service <service> -n <namespace>",
                "kubectl get endpoints -n <namespace>",
            ]
        )

    # ------------------------------------------------------------------------
    # Generic recommendation
    # ------------------------------------------------------------------------

    if not recommendations:
        recommendations.extend(
            [
                "Collect Kubernetes pod status.",
                "Collect Kubernetes events.",
                "Collect application logs.",
                "Check related deployments and services.",
            ]
        )

    # Generic commands for unknown/unrecognized symptoms.
    # Keep the recommendation useful even when no specific
    # troubleshooting rule matched the request.
    if not recommended_commands:
        recommended_commands.extend(
            [
                "kubectl get pods -A",
                "kubectl get deployments -A",
                "kubectl get services -A",
            ]
        )

    # Remove duplicates while preserving order
    recommendations = list(dict.fromkeys(recommendations))
    recommended_commands = list(dict.fromkeys(recommended_commands))

    final_response = (
        f"Diagnosis: {root_cause or 'Root cause not determined.'}\n\n"
        "Recommended troubleshooting actions:\n"
        + "\n".join(
            f"{index}. {recommendation}"
            for index, recommendation in enumerate(recommendations, start=1)
        )
    )

    return {
        "recommendations": recommendations,
        "recommended_commands": recommended_commands,
        "final_response": final_response,
        "verification_required": True,
        "error": None,
    }