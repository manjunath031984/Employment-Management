# AI Infrastructure Agent

## 1. Overview

The **AI Infrastructure Agent** is a standalone Python-based troubleshooting component added under:

```text
ai-infrastructure-agent/
```

Its purpose is to analyze infrastructure troubleshooting requests, inspect Kubernetes resources through read-only tools, diagnose common Kubernetes symptoms, and generate actionable troubleshooting recommendations.

The project is designed so that it can evolve toward an AI-assisted infrastructure operations workflow without modifying the existing Employment Management application.

## 2. Current Workflow

```text
START
  |
  v
ANALYZE
  |
  v
READ INFRASTRUCTURE
  |
  v
DIAGNOSE
  |
  v
RECOMMEND
  |
  v
END
```

### Analyze

The analysis node identifies:

- Kubernetes resource type
- Resource-related request information
- Common infrastructure symptoms
- Possible root causes

Supported resource types:

```text
Pod
Deployment
Service
Gateway
HTTPRoute
StatefulSet
PVC
```

Supported symptoms:

```text
CrashLoopBackOff
OOMKilled
Pending
ImagePullBackOff
ErrImagePull
connection refused
timeout
not ready
liveness failure
```

### Read Infrastructure

The current implementation is explicitly **read-only**.

The node currently provides a placeholder observation indicating that Kubernetes read-only tool integration will be connected in the Kubernetes integration phase.

No Kubernetes resources are modified by this node.

### Diagnose

The diagnosis node currently uses deterministic rules based on detected symptoms.

| Symptom | Current diagnosis confidence |
|---|---:|
| CrashLoopBackOff | 0.65 |
| OOMKilled | 0.85 |
| Pending | 0.70 |
| ImagePullBackOff / ErrImagePull | 0.85 |
| connection refused | 0.75 |
| Unknown/other | 0.30 |

### Recommend

The recommendation node is currently rule-based. It generates:

- Troubleshooting recommendations
- Suggested `kubectl` commands
- A final troubleshooting response
- A flag indicating that verification is required

For an unknown condition, generic read-only commands are recommended:

```bash
kubectl get pods -A
kubectl get deployments -A
kubectl get services -A
```

## 3. Project Structure

```text
ai-infrastructure-agent/
├── app/
│   ├── agent/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── prompts.py
│   │   └── state.py
│   ├── kubernetes/
│   │   └── client.py
│   ├── tools/
│   │   ├── deployment_tools.py
│   │   ├── gateway_tools.py
│   │   ├── kubernetes_tools.py
│   │   ├── pod_tools.py
│   │   └── service_tools.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_client.py
│   ├── test_deployment_tools.py
│   ├── test_gateway_tools.py
│   ├── test_graph.py
│   ├── test_kubernetes_tools.py
│   ├── test_main.py
│   ├── test_nodes.py
│   ├── test_pod_tools.py
│   ├── test_service_tools.py
│   └── test_state.py
├── .env.example
├── .gitignore
├── README.md
├── pytest.ini
└── requirements.txt
```

## 4. Kubernetes Integration

The Kubernetes client supports:

- In-cluster configuration
- Local kubeconfig
- `KUBECONFIG` environment variable
- Current Kubernetes context/namespace detection
- Kubernetes API client creation
- Kubernetes connectivity testing
- Cache reset for tests

The client exposes read-only API clients for:

```text
CoreV1Api
AppsV1Api
CustomObjectsApi
NetworkingV1Api
```

## 5. Kubernetes Troubleshooting Tools

### Kubernetes Tools

Provides read-only access for:

```text
Namespaces
Pods
Pod logs
Pod events
Deployments
Services
Endpoints
StatefulSets
PVCs
Gateways
HTTPRoutes
```

### Pod Tools

Supports:

- Pod inspection
- Pod listing
- Current container logs
- Previous container logs
- CrashLoopBackOff detection
- OOMKilled detection
- Restart problem detection
- Container status inspection
- Readiness checks
- Log size limiting

Secret values are not exposed by the tools.

### Deployment Tools

Supports:

- Deployment inspection
- Deployment listing
- Replica information
- Rollout status
- Deployment conditions
- Deployment problem detection
- Container information
- ReplicaSet inspection

Secret values are not exposed.

### Service Tools

Supports:

- Service inspection
- Service listing
- Endpoint inspection
- No-endpoint detection
- Service selector inspection
- Service port validation
- Full service investigation

### Gateway Tools

Supports:

- GatewayClass listing and inspection
- Gateway listing and inspection
- Gateway listeners
- Gateway conditions
- Gateway problem detection
- HTTPRoute listing and inspection
- HTTPRoute status
- HTTPRoute backend inspection
- HTTPRoute problem detection
- Gateway route investigation
- Gateway connectivity investigation

## 6. Agent State

The workflow uses `InfraState` to carry information through the graph.

The state includes fields for:

```text
user_request
namespace
resource_type
resource_name
observations
pods
events
logs
deployments
services
gateways
analysis
symptoms
possible_causes
diagnosis
root_cause
confidence
recommendations
recommended_commands
verification
final_response
error
```

## 7. Safety and Operating Model

The Kubernetes troubleshooting tools are designed to be **read-only**.

The current agent does not perform destructive or mutating Kubernetes actions such as:

```text
delete
apply
patch
scale
restart
rollout restart
secret modification
```

This is intentional so that investigation can be validated before introducing remediation automation.

## 8. Testing

The complete automated test suite was executed successfully:

```text
101 passed in 0.90s
```

The passing suite covers:

- Kubernetes client
- Kubernetes tools
- Pod tools
- Deployment tools
- Service tools
- Gateway tools
- Agent nodes
- Graph
- Main application entry point
- Agent state

Tests also validate that sensitive Kubernetes Secret values are not exposed.

Run the suite from the project directory with:

```bash
pytest -v
```

Expected current result:

```text
101 passed
```

## 9. Git / Repository Integration

The AI Infrastructure Agent was developed in the feature branch:

```text
feature/AI-Infrastructure-Agent
```

The branch was merged through GitHub into:

```text
feature/helm-chart
```

The AI agent remains isolated under the `ai-infrastructure-agent/` directory so that the existing Employment Management application remains independent.

## 10. Environment Files

The real `.env` file is intentionally excluded from Git.

The project uses:

```text
.env
.env.example
```

The `.gitignore` excludes:

```text
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
.venv/
venv/
.env
```

## 11. Technology Stack

Current project technologies include:

```text
Python
FastAPI
Uvicorn
Kubernetes Python Client
LangChain
LangGraph
LangChain OpenAI integration
Pydantic
python-dotenv
pytest
pytest-cov
```

## 12. Current Implementation Status

### Completed

- Standalone AI Infrastructure Agent directory
- LangGraph workflow
- Infrastructure state model
- Rule-based request analysis
- Rule-based diagnosis
- Rule-based recommendations
- Kubernetes client abstraction
- Read-only Kubernetes tools
- Pod troubleshooting tools
- Deployment troubleshooting tools
- Service troubleshooting tools
- Gateway / HTTPRoute troubleshooting tools
- Secret-value protection tests
- Graph tests
- Main application tests
- Complete test suite: **101/101 passing**
- Git integration into `feature/helm-chart`

### Current Limitation

The `read_infrastructure()` node currently contains placeholder behavior.

The next implementation phase is to connect that node to the existing read-only Kubernetes tools so the agent can investigate a real cluster instead of returning placeholder observations.

## 13. Next Phase

Recommended implementation sequence:

```text
1. Connect read_infrastructure() to Kubernetes tools
             |
             v
2. Connect real cluster credentials / kubeconfig
             |
             v
3. Investigate real Pods, Deployments, Services and Gateway resources
             |
             v
4. Feed observations into diagnosis
             |
             v
5. Produce evidence-based recommendations
             |
             v
6. Add verification of recommended remediation
```

A small GKE development cluster can then be used to validate real scenarios such as:

```text
CrashLoopBackOff
OOMKilled
Pending
ImagePullBackOff
Service without endpoints
Gateway not programmed
HTTPRoute backend problems
Readiness failures
Deployment rollout problems
```

## 14. Design Goal

```text
Natural Language Request
        |
        v
AI Infrastructure Agent
        |
        +--> Analyze
        |
        +--> Read Kubernetes
        |
        +--> Diagnose
        |
        +--> Recommend
        |
        +--> Verify
        |
        v
Infrastructure Troubleshooting Report
```

The design intentionally separates:

- Agent workflow
- Kubernetes client handling
- Kubernetes investigation tools
- State management
- Tests

This allows additional AI reasoning, observability integrations, remediation workflows, and verification capabilities to be added without coupling them directly to the existing Employment Management application.
