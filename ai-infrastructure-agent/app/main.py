"""
Main entry point for the AI Infrastructure Troubleshooting Agent.

Responsibilities:
- Start the troubleshooting agent
- Accept user requests
- Initialize InfraState
- Execute the LangGraph workflow
- Display the final diagnosis
- Display recommendations
- Provide Kubernetes connectivity check

Current workflow:

    USER REQUEST
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

IMPORTANT:
The current agent is READ-ONLY.

It does not:
- create Kubernetes resources
- modify Kubernetes resources
- delete Kubernetes resources
- restart workloads
- scale workloads
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from app.agent.graph import infra_graph
from app.agent.state import InfraState
from app.kubernetes.client import (
    get_current_kubernetes_context,
    test_kubernetes_connection,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "ai-infrastructure-agent"
)


# ---------------------------------------------------------------------------
# Agent Execution
# ---------------------------------------------------------------------------


def run_agent(
    user_request: str,
    namespace: str | None = None,
    resource: str | None = None,
    resource_type: str | None = None,
    resource_name: str | None = None,
) -> InfraState:
    """
    Execute the AI Infrastructure Troubleshooting Agent.

    Args:
        user_request:
            Natural-language troubleshooting request.

        namespace:
            Optional Kubernetes namespace.

        resource:
            Optional resource identifier.

        resource_type:
            Optional resource type.

        resource_name:
            Optional resource name.

    Returns:
        Final InfraState returned by LangGraph.
    """

    if not user_request.strip():

        raise ValueError(
            "Troubleshooting request cannot be empty."
        )

    initial_state: InfraState = {
        "user_request": user_request.strip(),
        "namespace": namespace,
        "resource": resource,
        "resource_type": resource_type,
        "resource_name": resource_name,
        "observations": [],
        "pods": [],
        "events": [],
        "logs": [],
        "deployments": [],
        "services": [],
        "gateways": [],
        "analysis": None,
        "symptoms": [],
        "possible_causes": [],
        "diagnosis": None,
        "root_cause": None,
        "confidence": 0.0,
        "recommendations": [],
        "recommended_commands": [],
        "verification_required": False,
        "verification_result": None,
        "final_response": None,
        "error": None,
    }

    logger.info(
        "Starting infrastructure troubleshooting."
    )

    logger.info(
        "Request: %s",
        user_request,
    )

    try:

        result = infra_graph.invoke(
            initial_state
        )

        logger.info(
            "Infrastructure troubleshooting completed."
        )

        return result

    except Exception as error:

        logger.exception(
            "Infrastructure troubleshooting failed."
        )

        return {
            **initial_state,
            "error": str(error),
            "final_response": (
                "The troubleshooting workflow failed.\n\n"
                f"Error: {error}"
            ),
        }


# ---------------------------------------------------------------------------
# Result Display
# ---------------------------------------------------------------------------


def display_result(
    result: InfraState,
) -> None:
    """
    Display the troubleshooting result in a readable format.
    """

    print()
    print("=" * 80)
    print("AI INFRASTRUCTURE TROUBLESHOOTING AGENT")
    print("=" * 80)

    # -----------------------------------------------------------------------
    # Request
    # -----------------------------------------------------------------------

    print()
    print("REQUEST")
    print("-" * 80)

    print(
        result.get(
            "user_request",
            "N/A",
        )
    )

    # -----------------------------------------------------------------------
    # Analysis
    # -----------------------------------------------------------------------

    print()
    print("ANALYSIS")
    print("-" * 80)

    print(
        result.get(
            "analysis",
            "No analysis available.",
        )
    )

    # -----------------------------------------------------------------------
    # Resource
    # -----------------------------------------------------------------------

    print()
    print("RESOURCE")
    print("-" * 80)

    print(
        f"Type      : "
        f"{result.get('resource_type') or 'Unknown'}"
    )

    print(
        f"Name      : "
        f"{result.get('resource_name') or 'Unknown'}"
    )

    print(
        f"Namespace : "
        f"{result.get('namespace') or 'Unknown'}"
    )

    # -----------------------------------------------------------------------
    # Symptoms
    # -----------------------------------------------------------------------

    print()
    print("DETECTED SYMPTOMS")
    print("-" * 80)

    symptoms = result.get(
        "symptoms",
        [],
    )

    if symptoms:

        for symptom in symptoms:

            print(
                f"- {symptom}"
            )

    else:

        print(
            "- No explicit symptoms detected."
        )

    # -----------------------------------------------------------------------
    # Possible Causes
    # -----------------------------------------------------------------------

    print()
    print("POSSIBLE CAUSES")
    print("-" * 80)

    possible_causes = result.get(
        "possible_causes",
        [],
    )

    if possible_causes:

        for cause in possible_causes:

            print(
                f"- {cause}"
            )

    else:

        print(
            "- No possible causes identified."
        )

    # -----------------------------------------------------------------------
    # Observations
    # -----------------------------------------------------------------------

    print()
    print("INFRASTRUCTURE OBSERVATIONS")
    print("-" * 80)

    observations = result.get(
        "observations",
        [],
    )

    if observations:

        for observation in observations:

            print(
                f"- {observation}"
            )

    else:

        print(
            "- No infrastructure observations."
        )

    # -----------------------------------------------------------------------
    # Diagnosis
    # -----------------------------------------------------------------------

    print()
    print("DIAGNOSIS")
    print("-" * 80)

    print(
        result.get(
            "diagnosis",
            "Diagnosis not available.",
        )
    )

    print()

    print(
        f"Root Cause : "
        f"{result.get('root_cause') or 'Not determined'}"
    )

    confidence = result.get(
        "confidence",
        0.0,
    )

    print(
        f"Confidence : "
        f"{confidence:.0%}"
    )

    # -----------------------------------------------------------------------
    # Recommendations
    # -----------------------------------------------------------------------

    print()
    print("RECOMMENDATIONS")
    print("-" * 80)

    recommendations = result.get(
        "recommendations",
        [],
    )

    if recommendations:

        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):

            print(
                f"{index}. {recommendation}"
            )

    else:

        print(
            "No recommendations available."
        )

    # -----------------------------------------------------------------------
    # Recommended Commands
    # -----------------------------------------------------------------------

    print()
    print("RECOMMENDED COMMANDS")
    print("-" * 80)

    commands = result.get(
        "recommended_commands",
        [],
    )

    if commands:

        for command in commands:

            print(
                f"$ {command}"
            )

    else:

        print(
            "No commands available."
        )

    # -----------------------------------------------------------------------
    # Error
    # -----------------------------------------------------------------------

    error = result.get(
        "error"
    )

    if error:

        print()
        print("ERROR")
        print("-" * 80)

        print(error)

    print()
    print("=" * 80)
    print("END OF TROUBLESHOOTING REPORT")
    print("=" * 80)
    print()


# ---------------------------------------------------------------------------
# Kubernetes Health Check
# ---------------------------------------------------------------------------


def check_kubernetes() -> int:
    """
    Test Kubernetes API connectivity.

    Returns:
        0 if successful.
        1 if connection fails.
    """

    print()
    print("=" * 80)
    print("KUBERNETES CONNECTION CHECK")
    print("=" * 80)

    result = test_kubernetes_connection()

    if result.get("success"):

        print()
        print("Status : CONNECTED")

        version = result.get(
            "version",
            {},
        )

        print(
            f"Version: "
            f"{version.get('git_version', 'Unknown')}"
        )

        context = get_current_kubernetes_context()

        if context.get("success"):

            context_data = context.get(
                "context",
                {},
            )

            print(
                f"Context: "
                f"{context_data.get('name', 'Unknown')}"
            )

            print(
                f"Cluster: "
                f"{context_data.get('cluster', 'Unknown')}"
            )

            print(
                f"Namespace: "
                f"{context_data.get('namespace', 'default')}"
            )

        print()

        return 0

    print()
    print("Status : FAILED")

    print(
        f"Error  : "
        f"{result.get('error', 'Unknown error')}"
    )

    print()

    return 1


# ---------------------------------------------------------------------------
# Interactive Mode
# ---------------------------------------------------------------------------


def interactive_mode() -> None:
    """
    Start interactive troubleshooting mode.
    """

    print()
    print("=" * 80)
    print("AI INFRASTRUCTURE TROUBLESHOOTING AGENT")
    print("=" * 80)

    print()
    print(
        "Enter an infrastructure troubleshooting request."
    )

    print(
        "Type 'exit' or 'quit' to stop."
    )

    print()

    while True:

        try:

            user_request = input(
                "You > "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError,
        ):

            print()
            print(
                "Exiting agent."
            )

            break

        if not user_request:

            continue

        if user_request.lower() in {
            "exit",
            "quit",
        }:

            print(
                "Exiting agent."
            )

            break

        try:

            result = run_agent(
                user_request
            )

            display_result(
                result
            )

        except Exception as error:

            print()
            print(
                f"Error: {error}"
            )
            print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argument_parser() -> argparse.ArgumentParser:
    """
    Build command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        description=(
            "AI Infrastructure Troubleshooting Agent"
        )
    )

    parser.add_argument(
        "request",
        nargs="?",
        help=(
            "Infrastructure troubleshooting request."
        ),
    )

    parser.add_argument(
        "--namespace",
        "-n",
        help=(
            "Kubernetes namespace."
        ),
    )

    parser.add_argument(
        "--resource-type",
        help=(
            "Kubernetes resource type, "
            "for example pod, deployment, service, "
            "gateway or httproute."
        ),
    )

    parser.add_argument(
        "--resource-name",
        help=(
            "Kubernetes resource name."
        ),
    )

    parser.add_argument(
        "--check-kubernetes",
        action="store_true",
        help=(
            "Check Kubernetes API connectivity."
        ),
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help=(
            "Start interactive troubleshooting mode."
        ),
    )

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """
    Application entry point.
    """

    parser = build_argument_parser()

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Kubernetes connection check
    # -----------------------------------------------------------------------

    if args.check_kubernetes:

        return check_kubernetes()

    # -----------------------------------------------------------------------
    # Interactive mode
    # -----------------------------------------------------------------------

    if args.interactive:

        interactive_mode()

        return 0

    # -----------------------------------------------------------------------
    # Single request mode
    # -----------------------------------------------------------------------

    if not args.request:

        parser.print_help()

        print()
        print(
            "Example:"
        )

        print(
            'python -m app.main '
            '"Why is my pod in CrashLoopBackOff?"'
        )

        print()

        return 1

    # -----------------------------------------------------------------------
    # Run agent
    # -----------------------------------------------------------------------

    result = run_agent(
        user_request=args.request,
        namespace=args.namespace,
        resource_type=args.resource_type,
        resource_name=args.resource_name,
    )

    display_result(
        result
    )

    if result.get("error"):

        return 1

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )