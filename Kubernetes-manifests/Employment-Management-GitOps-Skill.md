# Employment Management — GitHub Actions + Helm + Argo CD + GKE Skill Guide

## 1. Purpose

This guide documents the complete setup and troubleshooting flow used for the Employment Management application.

The final design uses:

- GitHub Actions for CI and image publishing
- Google Workload Identity Federation (OIDC) instead of a JSON service-account key
- Google Artifact Registry (GAR) for the application image
- GKE for Kubernetes
- Helm for application and platform manifests
- Argo CD for GitOps deployment
- GKE Gateway API for public routing
- PostgreSQL running inside GKE
- One public domain with path-based routing:
  - `https://cloudaiops.site/app/` → Employment Management
  - `https://cloudaiops.site/argocd/` → Argo CD

The Git branch used throughout the project is:

```text
feature/github-actions-ci
```

There is no separate `feature/helm-chart` branch in the final design.

---

# 2. Final Architecture

```text
                           GitHub
                              |
                              | push
                              v
                  GitHub Actions CI Pipeline
                              |
                              | OIDC / WIF
                              v
                  Google Cloud / GCP Project
                              |
                    +---------+---------+
                    |                   |
                    v                   v
             Artifact Registry       GKE Cluster
             employment-management  employment-management-gke
                    |                   |
                    | image             +---------------------------+
                    |                   |                           |
                    v                   v                           v
             Docker Image        stateful-demo namespace       GKE Gateway
             :1.0.x                     |                    8.233.81.181
                                        |
                         +--------------+----------------+
                         |                               |
                         v                               v
               Employment Management                 Argo CD
               Deployment                             Server
                         |                               |
                         v                               |
                    Spring Boot                         |
                         |                               |
                         v                               |
                    PostgreSQL                          |
                                                         |
                                                         |
                                                   Git repository
                                                         |
                                                         v
                                                   Kubernetes-manifests
```

Public routes:

```text
https://cloudaiops.site/app/
        |
        +--> Employment Management Service :8080

https://cloudaiops.site/argocd/
        |
        +--> Argo CD Service :80 -> container :8080
```

---

# 3. Project Information

| Item | Value |
|---|---|
| GitHub repository | `https://github.com/manjunath031984/Employment-Management.git` |
| Branch | `feature/github-actions-ci` |
| Helm path | `Kubernetes-manifests` |
| Namespace | `stateful-demo` |
| GKE cluster | `employment-management-gke` |
| GCP project | `gcp-dev-july-2026` |
| Region | `us-central1` |
| Domain | `cloudaiops.site` |
| Global static IP | `8.233.81.181` |
| Static IP resource | `cloudaiops-gateway-ip` |
| GatewayClass | `gke-l7-global-external-managed` |
| GAR repository | `employment-management` |
| GAR registry | `us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management` |
| Application image | `us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management` |
| Argo CD release | `argocd` |
| Argo CD namespace | `stateful-demo` |
| Application Helm release | `employment-management` |
| Application context path | `/app` |
| Application API | `/app/api/employees` |
| Argo CD path | `/argocd` |
| PostgreSQL database | `employee-managementdb` |
| PostgreSQL port | `5432` |

---

# 4. Important Design Decisions

## 4.1 One application branch

Only use:

```text
feature/github-actions-ci
```

GitHub Actions updates `Kubernetes-manifests/values.yaml` automatically when a new image is built.

## 4.2 One application ServiceAccount

The simplified design uses:

```text
stateful-demo/employment-management-sa
```

The application pods use this ServiceAccount. Argo CD's application controller also uses it.

Do not recreate the older, more complicated impersonation design.

Do not add these legacy files back:

```text
argocd-serviceaccount.yaml
argocd-application-controller-impersonator-clusterrole.yaml
argocd-application-controller-impersonator-clusterrolebinding.yaml
argocd-clusterrole.yaml
argocd-clusterrolebinding.yaml
```

## 4.3 Do not create a namespace template in the application chart

`stateful-demo` is shared by Argo CD and the application.

The application chart should not own the namespace.

Use an existing namespace or `--create-namespace` only when explicitly creating it.

## 4.4 Keep Argo CD values in the same `values.yaml`

The same `Kubernetes-manifests/values.yaml` contains:

- application values
- PostgreSQL values
- Gateway values
- RBAC values
- Argo CD Helm values

The application Helm chart ignores unrelated top-level keys, and the Argo CD chart ignores application-specific keys.

---

# 5. Recommended Repository Structure

```text
Employment-Management/
├── .github/
│   └── workflows/
├── Kubernetes-manifests/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       ├── gateway.yaml
│       ├── gatewayclass.yaml
│       ├── headless-service.yaml
│       ├── httproute.yaml
│       ├── postgres-configmap.yaml
│       ├── postgres-secret.yaml
│       ├── role.yaml
│       ├── rolebinding.yaml
│       ├── service.yaml
│       ├── serviceaccount.yaml
│       ├── statefulset.yaml
│       ├── tls-secret.yaml
│       └── argocd-healthcheckpolicy.yaml
├── src/
│   └── ...
├── Dockerfile
├── pom.xml
└── README.md
```

---

# 6. Application Path Configuration

This was a critical part of the deployment.

## 6.1 Spring Boot context path

`src/main/resources/application.properties` must contain:

```properties
server.port=8080
server.address=0.0.0.0
server.servlet.context-path=/app
```

## 6.2 Controller mapping

The controller must remain:

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {
```

Do NOT write:

```java
@RequestMapping("app/api/employees")
```

because Spring Boot already adds `/app` through the context path.

The resulting API is:

```text
/app/api/employees
```

## 6.3 Frontend API URL

`src/main/resources/static/script.js` must use:

```javascript
const API_BASE_URL = "/app/api/employees";
```

Do not use:

```javascript
const API_BASE_URL = "app/api/employees";
```

The leading `/` is important.

## 6.4 Final endpoint layout

```text
GET    /app/api/employees
POST   /app/api/employees
GET    /app/api/employees/{id}
PUT    /app/api/employees/{id}
DELETE /app/api/employees/{id}
```

---

# 7. Kubernetes Health Probes

Once Spring Boot runs under `/app`, Kubernetes probes must also use the `/app` path.

In `Kubernetes-manifests/templates/deployment.yaml`, all three probes must use:

```yaml
startupProbe:
  httpGet:
    path: /app/api/employees
    port: 8080

readinessProbe:
  httpGet:
    path: /app/api/employees
    port: 8080

livenessProbe:
  httpGet:
    path: /app/api/employees
    port: 8080
```

## Why this is required

If the application is configured with:

```properties
server.servlet.context-path=/app
```

and the probe checks:

```text
/api/employees
```

Spring Boot returns `404` to the probe. Kubernetes then restarts the container.

Observed symptom:

```text
Startup probe failed: HTTP probe failed with statuscode: 404
```

This caused the rollout to remain stuck until the probes were changed to `/app/api/employees`.

---

# 8. `values.yaml` Final Design

The application portion should look like this:

```yaml
app:
  replicaCount: 1
  image:
    repository: us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management
    tag: "1.0.9"
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8080
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

ServiceAccount:

```yaml
serviceAccount:
  create: true
  name: employment-management-sa
```

PostgreSQL:

```yaml
postgres:
  replicaCount: 1
  image:
    repository: postgres
    tag: "18"
    pullPolicy: IfNotPresent
  dbName: employee-managementdb
  user: postgres
  password: postgres
  port: 5432
  storage:
    className: standard-rwo
    size: 5Gi
```

Gateway:

```yaml
gateway:
  enabled: true
  className: gke-l7-global-external-managed
  ipName: cloudaiops-gateway-ip
  tlsSecretName: cloudaiops-tls
  tlsPasswordBase64: cG9zdGdyZXM=
  hostname: cloudaiops.site
  createClass: false
  appPath: /app
  argocdPath: /argocd
```

Argo CD Helm values in the same file:

```yaml
namespaceOverride: stateful-demo
createClusterRoles: true

controller:
  serviceAccount:
    create: false
    name: employment-management-sa

configs:
  cm:
    url: https://cloudaiops.site/argocd
    application.sync.impersonation.enabled: "false"
    application.sync.impersonation.enforced: "false"
  params:
    server.insecure: "true"
    server.basehref: /argocd
    server.rootpath: /argocd
```

---

# 9. HTTPRoute Configuration

The final route sends Argo CD and Employment Management through the same Gateway.

```yaml
{{- if .Values.gateway.enabled }}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: {{ printf "%s-route" .Release.Name | trunc 63 | trimSuffix "-" }}
  namespace: {{ .Release.Namespace }}
  labels:
    {{- include "employment-management.labels" . | nindent 4 }}

spec:
  hostnames:
    - {{ .Values.gateway.hostname | quote }}

  parentRefs:
    - name: {{ printf "%s-gateway" .Release.Name | trunc 63 | trimSuffix "-" }}
      kind: Gateway
      group: gateway.networking.k8s.io
      sectionName: https

  rules:
    - matches:
        - path:
            type: PathPrefix
            value: {{ .Values.gateway.argocdPath | quote }}
      backendRefs:
        - name: argocd-server
          port: 80

    - matches:
        - path:
            type: PathPrefix
            value: {{ .Values.gateway.appPath | quote }}
      backendRefs:
        - name: {{ include "employment-management.fullname" . }}
          port: {{ .Values.app.service.port }}
{{- end }}
```

Important: no URL rewrite is used for `/app`.

Spring Boot itself owns `/app` via `server.servlet.context-path=/app`.

---

# 10. GKE Gateway

Gateway details:

```text
Gateway: employment-management-gateway
GatewayClass: gke-l7-global-external-managed
Static IP resource: cloudaiops-gateway-ip
Static IP: 8.233.81.181
Hostname: cloudaiops.site
```

DNS must point:

```text
cloudaiops.site -> 8.233.81.181
```

Check the Gateway:

```bash
kubectl get gateway employment-management-gateway -n stateful-demo
```

Expected:

```text
PROGRAMMED   True
ADDRESS      8.233.81.181
```

Check the HTTPRoute:

```bash
kubectl get httproute employment-management-route \
  -n stateful-demo \
  -o jsonpath='{range .status.parents[0].conditions[*]}{.type}={.status} reason={.reason} message={.message}{"\n"}{end}'
```

Expected:

```text
ResolvedRefs=True
Accepted=True
Reconciled=True
```

---

# 11. GKE NEG / SNEG Troubleshooting

GKE Gateway uses standalone Network Endpoint Groups and ServiceNetworkEndpointGroups for Service backends.

Check SNEGs:

```bash
kubectl get servicenetworkendpointgroups.networking.gke.io -n stateful-demo
```

Describe the Employment Management SNEG:

```bash
kubectl describe servicenetworkendpointgroups.networking.gke.io \
  k8s1-17057d7b-stateful--employment-management-emplo-80-3163493f \
  -n stateful-demo
```

Healthy SNEG should show:

```text
Initialized=True
Synced=True
NEG State=ACTIVE
```

## Stale Argo CD NEG problem that occurred

An old Argo CD SNEG was stuck because the previous backend service still referenced it.

The backend service was deleted after the route was removed, and the old SNEG eventually disappeared.

When a stale Argo CD SNEG exists, do not manually manipulate it immediately. First verify:

```bash
gcloud compute backend-services list --global \
  --filter="name~argocd-server"
```

If the old backend dependency is gone, allow the NEG controller to reconcile.

## Clean Argo CD Service recreation

When the Argo CD Service was tied to a stale SNEG lifecycle, the clean recovery was:

```bash
kubectl delete svc argocd-server -n stateful-demo
```

then:

```bash
helm upgrade argocd argo/argo-cd \
  --namespace stateful-demo \
  -f Kubernetes-manifests/values.yaml
```

Verify:

```bash
kubectl get svc argocd-server -n stateful-demo
kubectl get servicenetworkendpointgroups.networking.gke.io -n stateful-demo
```

Do not delete the Gateway unnecessarily while troubleshooting the SNEG lifecycle.

---

# 12. Argo CD HealthCheckPolicy

Argo CD is exposed under `/argocd/`, but its root `/` returns `404`.

This caused the Google load balancer to report:

```text
no healthy upstream
```

The successful fix was a GKE `HealthCheckPolicy` targeted at `argocd-server`.

Create:

```text
Kubernetes-manifests/templates/argocd-healthcheckpolicy.yaml
```

with:

```yaml
apiVersion: networking.gke.io/v1
kind: HealthCheckPolicy
metadata:
  name: argocd-server-healthcheck
  namespace: {{ .Release.Namespace }}
spec:
  default:
    checkIntervalSec: 15
    timeoutSec: 5
    healthyThreshold: 1
    unhealthyThreshold: 2
    config:
      type: HTTP
      httpHealthCheck:
        port: 8080
        portSpecification: USE_FIXED_PORT
        requestPath: /argocd/
  targetRef:
    group: ""
    kind: Service
    name: argocd-server
```

Verify:

```bash
kubectl describe healthcheckpolicy argocd-server-healthcheck \
  -n stateful-demo
```

Expected:

```text
Type: Attached
Status: True
Reason: Attached
```

The event should also show that the controller successfully applied the policy.

## Important distinction

The Employment Management Service did not require a HealthCheckPolicy after the backend became healthy.

The Argo CD Service did require one because:

```text
http://argocd-server:8080/       -> 404
http://argocd-server:8080/argocd/ -> 200
```

---

# 13. Spring Boot API Verification

Local test through port-forward:

```bash
kubectl port-forward -n stateful-demo \
  svc/employment-management-employment-management 18081:8080
```

Then:

```bash
curl -i http://localhost:18081/app/api/employees
```

Expected:

```text
HTTP/1.1 200
Content-Type: application/json
```

An empty database returns:

```json
[]
```

If `18080` is occupied, use another local port such as `18081`.

---

# 14. Public Application Verification

Test the public API:

```bash
curl -k -i https://cloudaiops.site/app/api/employees
```

Expected:

```text
HTTP/1.1 200 OK
via: 1.1 google
```

Open the UI:

```text
https://cloudaiops.site/app/
```

---

# 15. Public Argo CD Verification

Test the Argo CD endpoint:

```bash
curl -k -i https://cloudaiops.site/argocd/
```

Expected:

```text
HTTP/1.1 200 OK
via: 1.1 google
```

Then open:

```text
https://cloudaiops.site/argocd/
```

The Argo CD UI should load.

---

# 16. Argo CD Admin Password

Get the initial admin password:

```bash
kubectl -n stateful-demo get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

Username:

```text
admin
```

Use:

```text
https://cloudaiops.site/argocd/
```

After changing to a preferred password, the initial secret can be removed according to the Argo CD installation guidance.

---

# 17. Create the Argo CD Application

In the Argo CD UI, create:

```text
Application Name: employment-management
Project: default
```

Source:

```text
Repository:
https://github.com/manjunath031984/Employment-Management.git

Revision:
feature/github-actions-ci

Path:
Kubernetes-manifests
```

Destination:

```text
Cluster:
https://kubernetes.default.svc

Namespace:
stateful-demo
```

Do not enable Auto-Create Namespace because the namespace already exists and is shared with Argo CD.

## Initial synchronization

After creating the application, the UI showed:

```text
Healthy
OutOfSync
```

Use **SYNC** and select `employment-management`.

Keep PRUNE enabled.

The final successful state was:

```text
Health: Healthy
Sync: Synced
```

---

# 18. Enable Argo CD Auto Sync

For the intended GitOps model, Automatic Sync should be enabled.

In the Argo CD application:

```text
App Details
  -> Sync Policy
  -> Automatic
```

Enable:

```text
Automatic Sync
Prune Resources
Self Heal
```

Do not enable namespace creation.

The desired final state is:

```text
Health: Healthy
Sync: Synced
Auto Sync: Enabled
```

---

# 19. GitHub Actions Image Flow

The workflow builds and pushes the application image to GAR.

The image naming convention is:

```text
us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management:<tag>
```

Image tags were generated from the GitHub Actions run number using the configured workflow logic.

Examples observed during the project:

```text
1.0.0
1.0.7
1.0.8
1.0.9
```

The workflow also updates the first application `tag:` entry in:

```text
Kubernetes-manifests/values.yaml
```

and commits the change with a message similar to:

```text
chore: update image tag to 1.0.x [skip ci]
```

This prevents the workflow's own values-file commit from creating an unnecessary recursive CI build.

---

# 20. Verify Artifact Registry

List images/tags using the Google Cloud UI or CLI.

Example CLI check:

```bash
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management \
  --include-tags
```

You should see the newly created application tags.

---

# 21. Deployment Flow After a Source Change

When application source code changes:

```text
1. Modify source
2. Commit to feature/github-actions-ci
3. git push
4. GitHub Actions starts
5. Tests/build run
6. Docker image is built
7. Image is pushed to GAR
8. values.yaml image tag is updated
9. Workflow commits/pushes values.yaml
10. Argo CD detects the Git change
11. Auto Sync applies the Helm chart
12. GKE performs rolling update
13. New pod becomes Ready
14. Gateway backend becomes healthy
15. Public endpoint serves the new version
```

---

# 22. Git Push Conflict Caused by GitHub Actions

Because GitHub Actions itself updates `values.yaml`, your local branch can become behind the remote branch.

If push fails with:

```text
rejected (fetch first)
remote contains work that you do not have locally
```

do not force-push.

Use:

```bash
git pull --rebase origin feature/github-actions-ci
```

Resolve conflicts if required, then:

```bash
git push origin feature/github-actions-ci
```

This preserves the automation-generated commits.

---

# 23. Rollout Troubleshooting

Check pods:

```bash
kubectl get pods -n stateful-demo
```

Check the Deployment image:

```bash
kubectl get deployment employment-management-employment-management \
  -n stateful-demo \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

Check rollout:

```bash
kubectl rollout status deployment/employment-management-employment-management \
  -n stateful-demo
```

If rollout reports:

```text
1 old replicas are pending termination
```

check the new and old pods:

```bash
kubectl get pods -n stateful-demo \
  -l app.kubernetes.io/instance=employment-management \
  -o wide
```

If the new pod is `0/1`, describe it:

```bash
kubectl describe pod POD_NAME -n stateful-demo
```

Look for:

```text
Startup probe failed
Readiness probe failed
Liveness probe failed
```

A previous failure was caused by probes checking `/api/employees` while the application had moved to `/app`.

---

# 24. Application Logs

Get logs:

```bash
kubectl logs -n stateful-demo \
  deployment/employment-management-employment-management \
  --tail=150
```

The logs showed PostgreSQL queries executing successfully, for example:

```text
Retrieved 0 employees from PostgreSQL
```

The generic exception handler originally logged only:

```text
An unexpected error occurred
```

When debugging a real application issue, consider logging the exception itself rather than only the generic message.

---

# 25. Gateway 503 Troubleshooting Checklist

If this returns `503`:

```bash
curl -k -i https://cloudaiops.site/app/api/employees
```

or:

```bash
curl -k -i https://cloudaiops.site/argocd/
```

check these layers in order.

## Layer 1 — Local Service

Employment:

```bash
kubectl port-forward -n stateful-demo \
  svc/employment-management-employment-management 18081:8080
```

Argo CD:

```bash
kubectl port-forward -n stateful-demo \
  svc/argocd-server 18082:80
```

Test the application directly.

## Layer 2 — EndpointSlice

Employment:

```bash
kubectl get endpointslice \
  -n stateful-demo \
  -l kubernetes.io/service-name=employment-management-employment-management \
  -o wide
```

Argo CD:

```bash
kubectl get endpointslice \
  -n stateful-demo \
  -l kubernetes.io/service-name=argocd-server \
  -o wide
```

## Layer 3 — SNEG

```bash
kubectl get servicenetworkendpointgroups.networking.gke.io \
  -n stateful-demo
```

## Layer 4 — Gateway and HTTPRoute

```bash
kubectl get gateway employment-management-gateway -n stateful-demo
```

```bash
kubectl get httproute employment-management-route \
  -n stateful-demo \
  -o jsonpath='{range .status.parents[0].conditions[*]}{.type}={.status} reason={.reason} message={.message}{"\n"}{end}'
```

Expected:

```text
ResolvedRefs=True
Accepted=True
Reconciled=True
```

## Layer 5 — Google Cloud backend health

List backend service:

```bash
gcloud compute backend-services list --global \
  --filter="name~argocd-server"
```

Check health:

```bash
gcloud compute backend-services get-health \
  BACKEND_SERVICE_NAME \
  --global
```

A backend endpoint should show:

```text
healthState: HEALTHY
```

---

# 26. Argo CD `no healthy upstream` Troubleshooting

If:

```text
https://cloudaiops.site/argocd/
```

returns:

```text
503 Service Unavailable
no healthy upstream
```

first test Argo CD locally:

```bash
kubectl port-forward -n stateful-demo svc/argocd-server 18082:80
```

Then:

```bash
curl -i http://localhost:18082/argocd/
```

Expected:

```text
HTTP/1.1 200 OK
```

Also test:

```bash
curl -i http://localhost:18082/
```

In this project:

```text
/argocd/ -> 200
/       -> 404
```

That proved the load balancer required a custom health check.

After creating `argocd-server-healthcheck`, verify:

```bash
kubectl describe healthcheckpolicy argocd-server-healthcheck \
  -n stateful-demo
```

Then:

```bash
gcloud compute backend-services get-health \
  gkegw1-ch6p-stateful-demo-argocd-server-80-x7ev8qzp4me9 \
  --global
```

The healthy backend eventually appeared as:

```text
10.112.129.16:8080
healthState: HEALTHY
```

After propagation:

```bash
curl -k -i https://cloudaiops.site/argocd/
```

returned `200 OK`.

---

# 27. Common Mistakes and Their Fixes

## Mistake 1 — Controller includes `/app`

Wrong:

```java
@RequestMapping("app/api/employees")
```

Correct:

```java
@RequestMapping("/api/employees")
```

Reason: Spring Boot context path already adds `/app`.

## Mistake 2 — Frontend API path is missing `/app`

Wrong:

```javascript
const API_BASE_URL = "/api/employees";
```

Correct:

```javascript
const API_BASE_URL = "/app/api/employees";
```

## Mistake 3 — Frontend uses a relative path without `/`

Wrong:

```javascript
const API_BASE_URL = "app/api/employees";
```

Correct:

```javascript
const API_BASE_URL = "/app/api/employees";
```

## Mistake 4 — Kubernetes probes still use `/api/employees`

Correct them to:

```text
/app/api/employees
```

## Mistake 5 — Assume a successful image push means GKE is already running it

Verify:

```bash
kubectl get deployment employment-management-employment-management \
  -n stateful-demo \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

Artifact Registry may already contain `1.0.9` while GKE is still running `1.0.8`.

## Mistake 6 — Force-push after GitHub Actions changes the branch

Use:

```bash
git pull --rebase origin feature/github-actions-ci
```

then push normally.

## Mistake 7 — Enable Auto-Create Namespace in Argo CD

Do not do this because `stateful-demo` is already used by Argo CD itself.

---

# 28. Useful Verification Commands

## Namespace

```bash
kubectl get namespace stateful-demo
```

## All application resources

```bash
kubectl get all -n stateful-demo
```

## Application Helm release

```bash
helm list -n stateful-demo
```

## Argo CD Helm release

```bash
helm list -n stateful-demo
```

## Gateway

```bash
kubectl get gateway -n stateful-demo
```

## HTTPRoute

```bash
kubectl get httproute -n stateful-demo
```

## Service

```bash
kubectl get svc -n stateful-demo
```

## Pods

```bash
kubectl get pods -n stateful-demo -o wide
```

## Image currently deployed

```bash
kubectl get deployment employment-management-employment-management \
  -n stateful-demo \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

---

# 29. Final Health Checklist

The environment is considered healthy when all of these are true.

## GitHub

```text
Branch: feature/github-actions-ci
Workflow: successful
values.yaml updated with latest image tag
```

## Artifact Registry

```text
Latest application image exists
```

## GKE

```text
Cluster: employment-management-gke
Namespace: stateful-demo
Application pod: 1/1 Running
PostgreSQL pod: 1/1 Running
```

## Gateway

```text
Programmed=True
GatewayHealthy=True
```

## HTTPRoute

```text
ResolvedRefs=True
Accepted=True
Reconciled=True
```

## Employment API

```text
https://cloudaiops.site/app/api/employees -> HTTP 200
```

## Employment UI

```text
https://cloudaiops.site/app/
```

## Argo CD

```text
https://cloudaiops.site/argocd/ -> HTTP 200
```

## Argo CD Application

```text
Application: employment-management
Health: Healthy
Sync: Synced
Auto Sync: Enabled
```

---

# 30. Complete GitOps Flow

Once Auto Sync is enabled, the intended day-to-day workflow becomes very small:

```bash
git checkout feature/github-actions-ci

git pull --rebase origin feature/github-actions-ci
```

Make application changes, then:

```bash
git add .
git commit -m "your change"
git push origin feature/github-actions-ci
```

Then monitor:

```text
GitHub Actions
    |
    +--> build/test
    |
    +--> push image to GAR
    |
    +--> update values.yaml
    |
    +--> commit image-tag update
    v
GitHub
    |
    v
Argo CD detects Git change
    |
    v
Automatic Sync
    |
    v
Helm upgrade in GKE
    |
    v
Rolling Deployment
    |
    v
Gateway backend healthy
    |
    v
https://cloudaiops.site/app/
```

---

# 31. Troubleshooting Order — Always Use This Order

When something breaks, do not change multiple components at once.

Use this order:

```text
1. Source code
2. Docker image
3. Artifact Registry
4. Deployment image
5. Pod state
6. Pod probes
7. Service
8. EndpointSlice
9. SNEG / NEG
10. Gateway
11. HTTPRoute
12. Google Cloud backend health
13. Public DNS / HTTPS endpoint
14. Argo CD synchronization state
```

This keeps troubleshooting deterministic and prevents unnecessary Gateway/NEG deletion.

---

# 32. End State

The completed platform provides:

```text
CI:
GitHub Actions

CD:
Argo CD

Container Registry:
Google Artifact Registry

Compute:
GKE

Packaging:
Helm

Ingress / Routing:
GKE Gateway API

Database:
PostgreSQL StatefulSet

Public Domain:
cloudaiops.site

Application:
https://cloudaiops.site/app/

Argo CD:
https://cloudaiops.site/argocd/
```

This is the baseline operating procedure for the project.
