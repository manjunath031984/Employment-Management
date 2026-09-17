# Employment Management -- GitHub Actions & Argo CD

## Project Title

**Cloud-Native Employment Management Platform -- CI/CD & GitOps using
GitHub Actions, Argo CD, Helm and GKE**

## Documentation File

`Employment-Management-GitHub-Actions-ArgoCD.md`

------------------------------------------------------------------------

# 1. Project Overview

This project deploys a containerized Employment Management application
on Google Kubernetes Engine (GKE) using a complete CI/CD and GitOps
workflow.

The implementation uses:

-   GitHub
-   GitHub Actions
-   Docker
-   Google Artifact Registry (GAR)
-   Helm
-   Argo CD
-   Google Kubernetes Engine (GKE)
-   Kubernetes Gateway API
-   GKE Gateway
-   HTTPRoute
-   PostgreSQL
-   Cloud DNS
-   HTTPS/TLS
-   Existing Google Cloud service account

The final application is exposed through:

`https://cloudaiops.site`

The Kubernetes namespace used by the application is:

`stateful-demo`

------------------------------------------------------------------------

# 2. Final Architecture

``` text
Developer
    |
    v
GitHub Repository
    |
    | Push / Pull Request
    v
GitHub Actions
    |
    +--> Build
    +--> Test
    +--> Docker Build
    +--> Authenticate to GCP
    +--> Push image
    |
    v
Google Artifact Registry
    |
    v
Helm / Kubernetes Manifests
    |
    v
Argo CD
    |
    | GitOps / Automated Sync
    v
GKE Cluster
    |
    +--> Namespace: stateful-demo
    |
    +--> Employment Management Deployment
    |
    +--> PostgreSQL StatefulSet
    |
    +--> ClusterIP Services
    |
    +--> GKE Gateway
    |
    +--> HTTPRoute
    |
    +--> TLS Secret
    |
    v
Global External Gateway IP
136.110.176.193
    |
    v
Cloud DNS
    |
    v
cloudaiops.site
    |
    v
Employment Management Application
```

------------------------------------------------------------------------

# 3. Important Project Values

  ---------------------------------------------------------------------------------------------------
  Item                                Value
  ----------------------------------- ---------------------------------------------------------------
  GCP Project                         `gcp-dev-july-2026`

  GKE Cluster                         `employment-management-gke`

  GKE Region                          `us-central1`

  Kubernetes Namespace                `stateful-demo`

  GitHub Repository                   `Employment-Management`

  Repository Owner                    `manjunath031984`

  GitOps Branch                       `feature/helm-chart`

  Kubernetes/Helm Path                `Kubernetes-manifests`

  Argo CD Application                 `employment-management`

  GatewayClass                        `gke-l7-global-external-managed`

  Static Gateway IP Name              `cloudaiops-gateway-ip`

  Static Gateway IP                   `136.110.176.193`

  Domain                              `cloudaiops.site`

  Application Port                    `8080`

  PostgreSQL Port                     `5432`

  PostgreSQL Database                 `studentdb`

  Container Registry                  Google Artifact Registry

  Image Repository                    `employment-management`

  Image Tag used                      `1.0.0`

  Argo CD Version                     `v3.5.3`

  Target Kubernetes Context           `gke_gcp-dev-july-2026_us-central1_employment-management-gke`
  ---------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 4. Repository

Repository:

`https://github.com/manjunath031984/Employment-Management.git`

The GitOps deployment uses:

``` text
Branch:
feature/helm-chart

Path:
Kubernetes-manifests
```

The repository contains the application and deployment-related files.

A typical Kubernetes/Helm directory contains files such as:

``` text
Kubernetes-manifests/
├── Chart.yaml
├── deployment.yaml
├── gateway.yaml
├── gatewayclass.yaml
├── headless-service.yaml
├── httproute.yaml
├── namespace.yaml
├── persistentvolumeclaim.yaml
├── postgres-configmap.yaml
├── postgres-secret.yaml
├── service.yaml
├── statefulset.yaml
├── PVC.md
└── GKE-Employment-Management-Destroy-Guide.md
```

Do not commit private credentials, service-account private keys,
passwords, or TLS private keys to Git.

------------------------------------------------------------------------

# 5. Git Branches Used

The project involved multiple branches during development.

Important branches:

``` text
main
feature/github-actions-ci
feature/helm-chart
feature/Employment-Management
feature/AI-Infrastructure-Troubleshooting-Agent
```

For the final Argo CD deployment, the important branch was:

``` text
feature/helm-chart
```

Argo CD was configured to monitor this branch.

------------------------------------------------------------------------

# 6. Google Cloud Project

Set the active project:

``` bash
gcloud config set project gcp-dev-july-2026
```

Verify:

``` bash
gcloud config get-value project
```

Expected:

``` text
gcp-dev-july-2026
```

------------------------------------------------------------------------

# 7. Required Google Cloud APIs

The project requires the relevant GKE, Artifact Registry, IAM, and
Gateway-related APIs.

Useful command:

``` bash
gcloud services list --enabled --project=gcp-dev-july-2026
```

The project previously enabled/used APIs including:

``` text
Cloud Resource Manager API
IAM API
IAM Service Account Credentials API
Security Token Service API
```

For the deployment workflow, also make sure the required container/GKE
APIs are enabled.

Example:

``` bash
gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  compute.googleapis.com \
  dns.googleapis.com \
  --project=gcp-dev-july-2026
```

------------------------------------------------------------------------

# 8. Existing Google Service Account

The project intentionally uses an **existing Google service account**
instead of creating another one.

Service account:

``` text
infra-admin@gcp-dev-july-2026.iam.gserviceaccount.com
```

The service account was used for infrastructure/GCP-related operations.

Important:

Do not create a new Google service account merely because Argo CD asks
about a Kubernetes service account.

These are different concepts.

### Google Cloud service account

Example:

``` text
infra-admin@gcp-dev-july-2026.iam.gserviceaccount.com
```

### Kubernetes service account

Example:

``` text
argocd-manager
```

The command:

``` bash
argocd cluster add ...
```

creates a Kubernetes service account named `argocd-manager` inside the
destination cluster so Argo CD can access that Kubernetes cluster.

This is separate from the existing Google Cloud service account.

------------------------------------------------------------------------

# 9. GKE Cluster

The final GKE cluster is:

``` text
employment-management-gke
```

Region:

``` text
us-central1
```

Verify:

``` bash
gcloud container clusters list \
  --project=gcp-dev-july-2026
```

Describe the cluster:

``` bash
gcloud container clusters describe employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026
```

------------------------------------------------------------------------

# 10. Configure kubectl for GKE

Get GKE credentials:

``` bash
gcloud container clusters get-credentials employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026
```

Verify:

``` bash
kubectl config current-context
```

Expected:

``` text
gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

List all contexts:

``` bash
kubectl config get-contexts
```

The project contained multiple contexts, including:

``` text
docker-desktop
gke_gcp-dev-july-2026_us-central1_employment-management-gke
gke_gcp-dev-july-2026_us-central1_gke-student-mgmt-dev
gke_gcp-dev-july-2026_us-central1_student-mgmt-dev
```

Always confirm the current context before executing destructive
commands.

------------------------------------------------------------------------

# 11. Kubernetes Namespace

The application uses only:

``` text
stateful-demo
```

Create it if it does not exist:

``` bash
kubectl create namespace stateful-demo
```

If the namespace already exists, the command will report that it already
exists.

Verify:

``` bash
kubectl get namespaces
```

Verify:

``` bash
kubectl get all -n stateful-demo
```

Initially, this returned:

``` text
No resources found in stateful-demo namespace.
```

This was expected before the Argo CD application was synchronized.

------------------------------------------------------------------------

# 12. Why Resources Were Not Present Initially

Creating an Argo CD Application does not necessarily mean the Kubernetes
workload already exists.

The GitOps sequence is:

``` text
Create Argo CD Application
        |
        v
Argo CD reads Git repository
        |
        v
Argo CD validates manifests
        |
        v
Argo CD synchronizes resources
        |
        v
Kubernetes resources are created
```

Therefore:

``` bash
kubectl get pods -n stateful-demo
```

can initially return:

``` text
No resources found
```

After a successful Argo CD sync, the pods appear.

------------------------------------------------------------------------

# 13. Argo CD Installation

Argo CD was installed in:

``` text
argocd
```

namespace.

Verify:

``` bash
kubectl get pods -n argocd
```

Expected components include:

``` text
argocd-application-controller
argocd-applicationset-controller
argocd-dex-server
argocd-notifications-controller
argocd-redis
argocd-repo-server
argocd-server
```

All components were eventually running.

------------------------------------------------------------------------

# 14. Argo CD CLI on Windows Git Bash

The Argo CD CLI was installed manually because Chocolatey was not
available.

Chocolatey commands returned:

``` text
bash: choco: command not found
```

The executable was installed at:

``` text
C:\Users\ASUS\bin\argocd.exe
```

Git Bash displayed:

``` text
/c/Users/ASUS/bin/argocd.exe
```

Verify:

``` bash
ls -lh ~/bin/argocd.exe
```

Verify the CLI:

``` bash
argocd version --client
```

The working version was:

``` text
argocd: v3.5.3
```

If Git Bash cannot find the executable, add the directory to PATH:

``` bash
export PATH="$HOME/bin:$PATH"
```

For permanent Git Bash configuration:

``` bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify again:

``` bash
argocd version --client
```

------------------------------------------------------------------------

# 15. Access Argo CD

Port-forward the Argo CD server:

``` bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open:

``` text
https://localhost:8080
```

The browser may show a certificate warning because this is a local
port-forward.

------------------------------------------------------------------------

# 16. Argo CD Initial Admin Password

The secret is:

``` text
argocd-initial-admin-secret
```

Command:

``` bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

If the command temporarily returned:

``` text
namespaces "argocd" not found
```

but the namespace later existed, verify first:

``` bash
kubectl get namespace argocd
```

Then retry the password command.

------------------------------------------------------------------------

# 17. Argo CD Login

Using the local port-forward:

``` bash
argocd login localhost:8080 --username admin --insecure
```

Enter the initial admin password.

Verify:

``` bash
argocd account get-user-info
```

------------------------------------------------------------------------

# 18. Add GKE Cluster to Argo CD

The current kubectl context was:

``` text
gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

Add it:

``` bash
argocd cluster add gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

Argo CD displayed a warning that the command creates:

``` text
argocd-manager
```

with cluster-level privileges.

After confirmation, it created:

``` text
ServiceAccount: argocd-manager
ClusterRole: argocd-manager-role
ClusterRoleBinding: argocd-manager-role-binding
Secret: argocd-manager-long-lived-token
```

This Kubernetes service account is used by Argo CD to manage resources
in the destination cluster.

Verify:

``` bash
argocd cluster list
```

The destination cluster appeared as:

``` text
https://35.226.2.92
```

------------------------------------------------------------------------

# 19. Important Argo CD Cluster Status Note

Immediately after adding a cluster, this message can appear:

``` text
Cluster has no applications and is not being monitored.
```

This does not necessarily mean the cluster connection is broken.

It can simply mean no Argo CD Application is currently using that
cluster.

Once the Application is configured and synchronized, the cluster becomes
actively used.

------------------------------------------------------------------------

# 20. Google Artifact Registry

The Artifact Registry repository used by the application is:

``` text
employment-management
```

Region:

``` text
us-central1
```

Project:

``` text
gcp-dev-july-2026
```

List repositories:

``` bash
gcloud artifacts repositories list \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

Expected repository:

``` text
employment-management
```

------------------------------------------------------------------------

# 21. Docker Registry Authentication

Configure Docker authentication:

``` bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Expected message:

``` text
Adding credentials for: us-central1-docker.pkg.dev
```

The configuration was successfully registered.

------------------------------------------------------------------------

# 22. Docker Image

The application image repository is:

``` text
us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management
```

Example image tag:

``` text
1.0.0
```

Complete image:

``` text
us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management:1.0.0
```

Build:

``` bash
docker build -t employment-management:1.0.0 .
```

Tag:

``` bash
docker tag employment-management:1.0.0 \
  us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management:1.0.0
```

Push:

``` bash
docker push \
  us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management:1.0.0
```

Verify:

``` bash
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management \
  --include-tags
```

------------------------------------------------------------------------

# 23. GitHub Actions CI

GitHub Actions is responsible for the CI portion.

The workflow is stored under:

``` text
.github/workflows/
```

Typical CI sequence:

``` text
Checkout source
      |
      v
Set up Java
      |
      v
Build application
      |
      v
Run tests
      |
      v
Build Docker image
      |
      v
Authenticate to GCP
      |
      v
Push image to Artifact Registry
```

The exact workflow should use GitHub Secrets/Variables for sensitive
configuration.

Never place:

-   Google private keys
-   database passwords
-   TLS private keys
-   API keys

directly into source-controlled files.

------------------------------------------------------------------------

# 24. Helm Chart

The Kubernetes deployment was packaged/organized using Helm.

Important files:

``` text
Kubernetes-manifests/
├── Chart.yaml
├── values.yaml
└── templates/
```

Helm allows values such as:

``` text
image repository
image tag
replica count
service port
service type
resource requests
resource limits
gateway class
gateway IP
hostname
TLS secret
```

to be parameterized instead of hard-coded.

------------------------------------------------------------------------

# 25. Helm Values Used

Important application values included:

``` text
app.image.tag = 1.0.0

app.image.pullPolicy = IfNotPresent

app.image.repository =
us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management

app.replicaCount = 1

app.service.port = 8080

app.service.type = ClusterIP

app.resources.requests.cpu = 250m

app.resources.requests.memory = 256Mi

app.resources.limits.cpu = 500m

app.resources.limits.memory = 512Mi
```

Gateway:

``` text
gateway.className = gke-l7-global-external-managed
```

Gateway IP:

``` text
cloudaiops-gateway-ip
```

------------------------------------------------------------------------

# 26. PostgreSQL

The application uses PostgreSQL.

It does not use Google Cloud SQL.

PostgreSQL is deployed inside Kubernetes using a StatefulSet.

The PostgreSQL workload includes:

``` text
StatefulSet
Headless Service
ConfigMap
Secret
PersistentVolumeClaim
```

Application port:

``` text
8080
```

PostgreSQL port:

``` text
5432
```

Database:

``` text
studentdb
```

------------------------------------------------------------------------

# 27. PostgreSQL Kubernetes Resources

Verify:

``` bash
kubectl get statefulset -n stateful-demo
```

Verify:

``` bash
kubectl get pods -n stateful-demo
```

Verify:

``` bash
kubectl get svc -n stateful-demo
```

The final PostgreSQL pod was:

``` text
employment-management-postgres-0
```

The PostgreSQL service was:

``` text
employment-management-postgres
```

The service is headless:

``` text
ClusterIP: None
```

------------------------------------------------------------------------

# 28. Employment Management Kubernetes Resources

The application deployment was:

``` text
employment-management-employment-management
```

The application service was:

``` text
employment-management-employment-management
```

Service type:

``` text
ClusterIP
```

Port:

``` text
8080
```

Verify:

``` bash
kubectl get deployment -n stateful-demo
kubectl get pods -n stateful-demo
kubectl get svc -n stateful-demo
```

------------------------------------------------------------------------

# 29. Kubernetes Gateway API

Initially, this command returned:

``` text
error: the server doesn't have a resource type "gatewayclass"
```

This happened because Gateway API support had not yet been
available/configured on the selected cluster.

The GKE Gateway API configuration was checked using:

``` bash
gcloud container clusters describe employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026 \
  --format="value(networkConfig.gatewayApiConfig)"
```

The result showed:

``` text
channel=CHANNEL_STANDARD
```

After Gateway API support became available, verify:

``` bash
kubectl get gatewayclass
```

The cluster returned GatewayClasses including:

``` text
gke-l7-global-external-managed
gke-l7-gxlb
gke-l7-regional-external-managed
gke-l7-rilb
```

The selected GatewayClass is:

``` text
gke-l7-global-external-managed
```

------------------------------------------------------------------------

# 30. Static IP for GKE Gateway

A previous static IP existed:

``` text
employment-management-ip
```

Its address was:

``` text
34.36.234.203
```

A new static global IP was created for the Gateway:

``` text
cloudaiops-gateway-ip
```

The final address is:

``` text
136.110.176.193
```

Verify:

``` bash
gcloud compute addresses describe cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026 \
  --format="yaml(name,address,status)"
```

Expected:

``` text
address: 136.110.176.193
name: cloudaiops-gateway-ip
status: RESERVED
```

------------------------------------------------------------------------

# 31. Delete the Old Static IP

The old address was no longer required.

Delete it with:

``` bash
gcloud compute addresses delete employment-management-ip \
  --global \
  --project=gcp-dev-july-2026
```

Confirm when prompted.

List addresses:

``` bash
gcloud compute addresses list \
  --global \
  --project=gcp-dev-july-2026
```

The intended remaining Gateway address is:

``` text
cloudaiops-gateway-ip
```

Do not delete `cloudaiops-gateway-ip` while the Gateway is using it.

------------------------------------------------------------------------

# 32. Gateway Manifest

The Gateway uses:

``` yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
```

The important configuration is:

``` yaml
metadata:
  name: employment-management-gateway
  namespace: stateful-demo

spec:
  gatewayClassName: gke-l7-global-external-managed

  addresses:
    - type: NamedAddress
      value: cloudaiops-gateway-ip
```

The HTTPS listener uses:

``` text
Port: 443
Protocol: HTTPS
```

TLS certificate secret:

``` text
cloudaiops-tls
```

------------------------------------------------------------------------

# 33. Gateway IP Error and Resolution

During the first deployment, Gateway status showed:

``` text
Error GWCER106:
address "cloudaiops-gateway-ip" does not exist
```

At that point, the Kubernetes Gateway referred to a named Google Cloud
address that had not yet been created.

The fix was:

1.  Create the global static IP.
2.  Use the exact name: `cloudaiops-gateway-ip`
3.  Keep the Gateway manifest using: `NamedAddress`
4.  Wait for GKE Gateway controller reconciliation.
5.  Verify the Gateway.

Verification:

``` bash
kubectl get gateway employment-management-gateway -n stateful-demo
```

Final successful result:

``` text
NAME                            CLASS                            ADDRESS           PROGRAMMED
employment-management-gateway   gke-l7-global-external-managed   136.110.176.193   True
```

------------------------------------------------------------------------

# 34. DNS A Record

The domain is:

``` text
cloudaiops.site
```

The A record must point to:

``` text
136.110.176.193
```

Final DNS relationship:

``` text
cloudaiops.site
       |
       A
       |
       v
136.110.176.193
```

Do not point the domain to the old address:

``` text
34.36.234.203
```

After creating/updating the A record, verify:

``` bash
nslookup cloudaiops.site
```

or:

``` bash
dig cloudaiops.site
```

DNS propagation can take time depending on TTL and DNS provider
behavior.

------------------------------------------------------------------------

# 35. TLS Secret

The Gateway uses:

``` text
cloudaiops-tls
```

Verify:

``` bash
kubectl get secret cloudaiops-tls -n stateful-demo
```

The secret must contain the certificate and private key expected by the
Gateway.

Important:

Do not commit the TLS private key into GitHub.

If the TLS secret is generated outside Kubernetes/Argo CD, make sure it
exists in:

``` text
stateful-demo
```

before the Gateway requires it.

------------------------------------------------------------------------

# 36. HTTPRoute

The HTTPRoute is:

``` text
employment-management-route
```

Namespace:

``` text
stateful-demo
```

Hostname:

``` text
cloudaiops.site
```

Path:

``` text
/
```

Backend service:

``` text
employment-management-employment-management
```

Backend port:

``` text
8080
```

The route references:

``` text
employment-management-gateway
```

listener:

``` text
https
```

------------------------------------------------------------------------

# 37. HTTPRoute Validation

Run:

``` bash
kubectl describe httproute employment-management-route \
  -n stateful-demo
```

The successful status included:

``` text
Reason: ResolvedRefs
Status: True
```

and:

``` text
Reason: Accepted
Status: True
```

The controller reported that object references were successfully
resolved and the HTTPRoute was successfully bound to the Gateway.

This confirms that:

``` text
HTTPRoute
    |
    v
Gateway
    |
    v
Service
```

is correctly connected.

------------------------------------------------------------------------

# 38. Argo CD Application

The final Argo CD Application name is:

``` text
employment-management
```

Create/configure the Application with:

``` text
Application Name:
employment-management
```

Project:

``` text
default
```

Repository:

``` text
https://github.com/manjunath031984/Employment-Management.git
```

Revision:

``` text
feature/helm-chart
```

Path:

``` text
Kubernetes-manifests
```

Destination cluster:

``` text
gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

Destination namespace:

``` text
stateful-demo
```

Sync policy:

``` text
Automated
```

Prune:

``` text
Enabled
```

------------------------------------------------------------------------

# 39. Argo CD Application Configuration

The critical mapping is:

``` text
Git Repository
    |
    +--> Branch: feature/helm-chart
    |
    +--> Path: Kubernetes-manifests
             |
             v
         Argo CD
             |
             v
Destination:
employment-management-gke
             |
             v
Namespace:
stateful-demo
```

The application must use:

``` text
stateful-demo
```

and not another application namespace.

------------------------------------------------------------------------

# 40. Argo CD Synchronization

Check:

``` bash
argocd app get employment-management
```

Manual synchronization:

``` bash
argocd app sync employment-management
```

Refresh:

``` bash
argocd app refresh employment-management
```

If `argocd app refresh` does not behave as expected, synchronization can
still be triggered with:

``` bash
argocd app sync employment-management
```

The Argo CD UI also provides:

``` text
SYNC
REFRESH
```

buttons.

------------------------------------------------------------------------

# 41. Initial Argo CD Sync Failure

The first synchronization failed because the destination cluster did not
yet expose:

``` text
gateway.networking.k8s.io/v1
```

Argo CD reported:

``` text
failed to discover server resources for group version
gateway.networking.k8s.io/v1
```

It also reported that:

``` text
Gateway
HTTPRoute
```

CRDs/resources could not be found.

The resolution was to make Gateway API support available on the GKE
cluster and verify:

``` bash
kubectl get gatewayclass
```

After Gateway API became available, synchronization succeeded.

------------------------------------------------------------------------

# 42. Successful Argo CD Synchronization

Final command:

``` bash
argocd app get employment-management
```

Final state:

``` text
Sync Status:   Synced to feature/helm-chart
Health Status: Healthy
```

The synchronized resources included:

``` text
Secret
ConfigMap
Service
Deployment
StatefulSet
Gateway
HTTPRoute
```

The final state was:

``` text
Synced + Healthy
```

------------------------------------------------------------------------

# 43. Verify All Kubernetes Resources

Run:

``` bash
kubectl get all -n stateful-demo
```

The successful deployment contained:

``` text
Pod:
employment-management-employment-management-57cc64fb47-pxgwl

Pod:
employment-management-postgres-0

Service:
employment-management-employment-management

Service:
employment-management-postgres

Deployment:
employment-management-employment-management

StatefulSet:
employment-management-postgres
```

------------------------------------------------------------------------

# 44. Verify Pods

``` bash
kubectl get pods -n stateful-demo
```

Expected:

``` text
employment-management-employment-management-xxxxx   1/1   Running
employment-management-postgres-0                     1/1   Running
```

A pod should show:

``` text
READY 1/1
STATUS Running
```

------------------------------------------------------------------------

# 45. Verify Services

``` bash
kubectl get svc -n stateful-demo
```

Expected application service:

``` text
employment-management-employment-management
ClusterIP
8080/TCP
```

Expected PostgreSQL service:

``` text
employment-management-postgres
ClusterIP
5432/TCP
```

------------------------------------------------------------------------

# 46. Verify Gateway

``` bash
kubectl get gateway -n stateful-demo
```

Expected:

``` text
employment-management-gateway
gke-l7-global-external-managed
136.110.176.193
True
```

The most important fields are:

``` text
ADDRESS = 136.110.176.193
PROGRAMMED = True
```

------------------------------------------------------------------------

# 47. Verify HTTPRoute

``` bash
kubectl get httproute -n stateful-demo
```

Expected:

``` text
employment-management-route
```

Describe it:

``` bash
kubectl describe httproute employment-management-route \
  -n stateful-demo
```

Verify:

``` text
Accepted: True
ResolvedRefs: True
```

------------------------------------------------------------------------

# 48. Verify Gateway Details

``` bash
kubectl describe gateway employment-management-gateway \
  -n stateful-demo
```

Important successful values:

``` text
Gateway Class:
gke-l7-global-external-managed

Address:
cloudaiops-gateway-ip

Resolved IP:
136.110.176.193

Listener:
https

Port:
443

Protocol:
HTTPS

TLS Secret:
cloudaiops-tls
```

------------------------------------------------------------------------

# 49. Verify DNS

Run:

``` bash
nslookup cloudaiops.site
```

The DNS response should resolve to:

``` text
136.110.176.193
```

If it still resolves to the old address, check the DNS A record and wait
for propagation.

------------------------------------------------------------------------

# 50. Verify the Application

Open:

``` text
https://cloudaiops.site
```

The final application successfully displayed:

``` text
Employment Management
Spring Boot CRUD Practice Application
```

The UI showed:

``` text
API Connected
```

and:

``` text
PostgreSQL Active
```

Employee data was also displayed.

This confirms the complete path is working:

``` text
Internet
   |
   v
cloudaiops.site
   |
   v
136.110.176.193
   |
   v
GKE Gateway
   |
   v
HTTPRoute
   |
   v
ClusterIP Service
   |
   v
Employment Management Pod
   |
   v
PostgreSQL
```

------------------------------------------------------------------------

# 51. Application Health Verification

Use:

``` bash
kubectl get pods -n stateful-demo
```

``` bash
kubectl get svc -n stateful-demo
```

``` bash
kubectl get gateway -n stateful-demo
```

``` bash
kubectl get httproute -n stateful-demo
```

``` bash
argocd app get employment-management
```

The desired final state is:

``` text
Pods:       Running
Services:   Healthy
Gateway:    PROGRAMMED=True
HTTPRoute:  Accepted=True
Argo CD:    Synced
Argo CD:    Healthy
```

------------------------------------------------------------------------

# 52. GitOps Operating Model

After the initial deployment, application changes should normally be
made through Git.

Do not manually modify the live Kubernetes deployment unless
troubleshooting requires it.

Recommended workflow:

``` text
1. Developer changes source code
2. Commit changes
3. Push to GitHub
4. GitHub Actions runs
5. Build and test
6. Build Docker image
7. Push image to GAR
8. Update deployment/Helm image version
9. Commit/push Git change
10. Argo CD detects Git change
11. Argo CD synchronizes
12. GKE rolls out the new version
```

------------------------------------------------------------------------

# 53. CI vs CD Responsibilities

## GitHub Actions -- CI

GitHub Actions is responsible for:

``` text
Source checkout
Build
Unit tests
Docker build
Container authentication
Artifact Registry push
```

## Argo CD -- CD / GitOps

Argo CD is responsible for:

``` text
Watching Git
Comparing desired state
Synchronizing Kubernetes resources
Automated deployment
Pruning removed resources
Reporting health
```

This creates a clean separation:

``` text
GitHub Actions = CI
Argo CD        = CD/GitOps
```

------------------------------------------------------------------------

# 54. Why Argo CD Was Used

Argo CD provides:

-   Git as the source of truth
-   Kubernetes desired-state reconciliation
-   Automated synchronization
-   Drift detection
-   Deployment visibility
-   Resource health information
-   Rollback support
-   GitOps workflow

The final Application showed:

``` text
Synced
Healthy
```

which confirms that the live cluster matched the desired Git state.

------------------------------------------------------------------------

# 55. Why Helm Was Used

Helm provides:

-   Parameterization
-   Reusable templates
-   Versioned application packaging
-   Easier environment-specific configuration
-   Cleaner Kubernetes deployment management

Examples of values that can be parameterized:

``` text
replicaCount
image.repository
image.tag
service.port
resources
gatewayClassName
gateway IP name
hostname
TLS secret
```

------------------------------------------------------------------------

# 56. Why GKE Gateway API Was Used

The project uses:

``` text
GKE Gateway API
```

instead of exposing the application directly with a Kubernetes
`LoadBalancer` service.

The traffic path is:

``` text
HTTPS
  |
  v
GKE Gateway
  |
  v
HTTPRoute
  |
  v
ClusterIP Service
  |
  v
Application Pod
```

This provides a clean separation between:

``` text
External traffic entry
Routing rules
Application service
Application pods
```

------------------------------------------------------------------------

# 57. Important Namespace Rule

The application uses only:

``` text
stateful-demo
```

Therefore application resources should be checked with:

``` bash
kubectl get all -n stateful-demo
```

Gateway:

``` bash
kubectl get gateway -n stateful-demo
```

HTTPRoute:

``` bash
kubectl get httproute -n stateful-demo
```

Secrets:

``` bash
kubectl get secrets -n stateful-demo
```

ConfigMaps:

``` bash
kubectl get configmaps -n stateful-demo
```

Do not accidentally deploy the application into:

``` text
default
```

or:

``` text
argocd
```

------------------------------------------------------------------------

# 58. Important Context Safety

Before running Kubernetes commands, always check:

``` bash
kubectl config current-context
```

Expected:

``` text
gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

For Argo CD:

``` bash
argocd app get employment-management
```

Confirm the server is the intended GKE cluster.

This is especially important before:

``` bash
kubectl delete
argocd app delete
gcloud container clusters delete
```

------------------------------------------------------------------------

# 59. Troubleshooting -- Argo CD Shows Missing

Check:

``` bash
argocd app get employment-management
```

Then:

``` bash
kubectl get pods -n stateful-demo
```

Then:

``` bash
argocd app sync employment-management
```

If resources are still missing, inspect:

``` bash
argocd app logs employment-management
```

and:

``` bash
kubectl describe pod <pod-name> -n stateful-demo
```

------------------------------------------------------------------------

# 60. Troubleshooting -- GatewayClass Not Found

Error:

``` text
the server doesn't have a resource type "gatewayclass"
```

Check:

``` bash
kubectl api-resources | grep -i gateway
```

Then:

``` bash
kubectl get gatewayclass
```

Also check GKE Gateway API configuration:

``` bash
gcloud container clusters describe employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026 \
  --format="value(networkConfig.gatewayApiConfig)"
```

Once Gateway API is available, verify the GatewayClasses.

------------------------------------------------------------------------

# 61. Troubleshooting -- Gateway Address Does Not Exist

Error:

``` text
Error GWCER106:
address "cloudaiops-gateway-ip" does not exist
```

Check:

``` bash
gcloud compute addresses describe cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026
```

The address must exist as a global address.

Then check:

``` bash
kubectl get gateway employment-management-gateway \
  -n stateful-demo
```

GKE should eventually show:

``` text
ADDRESS           PROGRAMMED
136.110.176.193   True
```

------------------------------------------------------------------------

# 62. Troubleshooting -- HTTPRoute

Check:

``` bash
kubectl describe httproute employment-management-route \
  -n stateful-demo
```

Verify:

``` text
Accepted: True
ResolvedRefs: True
```

If `ResolvedRefs` is false, check:

-   Service name
-   Service port
-   Gateway name
-   Gateway namespace
-   Listener name
-   Backend service existence

------------------------------------------------------------------------

# 63. Troubleshooting -- Pods Not Running

Check:

``` bash
kubectl get pods -n stateful-demo
```

Describe:

``` bash
kubectl describe pod <pod-name> -n stateful-demo
```

Check logs:

``` bash
kubectl logs <pod-name> -n stateful-demo
```

For previous container logs:

``` bash
kubectl logs <pod-name> -n stateful-demo --previous
```

Check events:

``` bash
kubectl get events -n stateful-demo --sort-by=.lastTimestamp
```

------------------------------------------------------------------------

# 64. Troubleshooting -- PostgreSQL

Check:

``` bash
kubectl get pod employment-management-postgres-0 \
  -n stateful-demo
```

Logs:

``` bash
kubectl logs employment-management-postgres-0 \
  -n stateful-demo
```

Check StatefulSet:

``` bash
kubectl describe statefulset employment-management-postgres \
  -n stateful-demo
```

Check PVC:

``` bash
kubectl get pvc -n stateful-demo
```

------------------------------------------------------------------------

# 65. Troubleshooting -- Application

Check deployment:

``` bash
kubectl get deployment \
  employment-management-employment-management \
  -n stateful-demo
```

Check logs:

``` bash
kubectl logs deployment/employment-management-employment-management \
  -n stateful-demo
```

Check service:

``` bash
kubectl describe svc \
  employment-management-employment-management \
  -n stateful-demo
```

Check endpoints:

``` bash
kubectl get endpoints \
  employment-management-employment-management \
  -n stateful-demo
```

------------------------------------------------------------------------

# 66. Troubleshooting -- Argo CD OutOfSync

Run:

``` bash
argocd app get employment-management
```

If:

``` text
OutOfSync
```

run:

``` bash
argocd app refresh employment-management
```

Then:

``` bash
argocd app sync employment-management
```

If the resource was manually changed, compare the live state with Git
and decide whether Git should be updated or the live change should be
removed.

------------------------------------------------------------------------

# 67. Troubleshooting -- Argo CD Repository

Check Application:

``` bash
argocd app get employment-management
```

Confirm:

``` text
Repo:
https://github.com/manjunath031984/Employment-Management.git

Target:
feature/helm-chart

Path:
Kubernetes-manifests
```

If the wrong branch/path is configured, Argo CD will not deploy the
intended manifests.

------------------------------------------------------------------------

# 68. Troubleshooting -- Docker/GAR Authentication

Run:

``` bash
gcloud auth list
```

Set the correct project:

``` bash
gcloud config set project gcp-dev-july-2026
```

Configure Docker:

``` bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Verify:

``` bash
gcloud artifacts repositories list \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

Then retry:

``` bash
docker push \
  us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management:1.0.0
```

------------------------------------------------------------------------

# 69. Security Rules

Never commit these to Git:

``` text
*.json service-account credentials
private keys
TLS private keys
database passwords
API keys
OpenAI keys
GitHub tokens
access tokens
```

The earlier service-account JSON contained a private key and therefore
should never be committed to a public repository.

If a private key has ever been exposed publicly, rotate/revoke it
immediately and replace it with a safer authentication mechanism.

------------------------------------------------------------------------

# 70. Production Improvement -- Workload Identity

For production, prefer keyless authentication such as:

``` text
Workload Identity Federation
```

instead of long-lived Google service-account JSON keys.

The project also explored:

``` text
Jenkins
Keycloak
OIDC
Workload Identity Federation
```

These are useful for secure CI/CD authentication.

------------------------------------------------------------------------

# 71. Final Verification Checklist

Run all of the following before declaring the deployment complete.

## GCP

``` bash
gcloud config get-value project
```

Expected:

``` text
gcp-dev-july-2026
```

## GKE

``` bash
kubectl config current-context
```

Expected:

``` text
gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

## Namespace

``` bash
kubectl get namespace stateful-demo
```

## Pods

``` bash
kubectl get pods -n stateful-demo
```

Expected:

``` text
Running
```

## Services

``` bash
kubectl get svc -n stateful-demo
```

Expected:

``` text
Application: 8080
PostgreSQL: 5432
```

## GatewayClass

``` bash
kubectl get gatewayclass
```

Expected:

``` text
gke-l7-global-external-managed
```

## Gateway

``` bash
kubectl get gateway -n stateful-demo
```

Expected:

``` text
ADDRESS: 136.110.176.193
PROGRAMMED: True
```

## HTTPRoute

``` bash
kubectl get httproute -n stateful-demo
```

## DNS

``` bash
nslookup cloudaiops.site
```

Expected:

``` text
136.110.176.193
```

## Argo CD

``` bash
argocd app get employment-management
```

Expected:

``` text
Sync Status: Synced
Health Status: Healthy
```

## Browser

Open:

``` text
https://cloudaiops.site
```

Expected:

``` text
Employment Management
API Connected
PostgreSQL Active
```

------------------------------------------------------------------------

# 72. Final Deployment Status

The final implementation successfully achieved:

``` text
GitHub
   |
   v
GitHub Actions
   |
   v
Docker Image
   |
   v
Google Artifact Registry
   |
   v
Helm
   |
   v
Argo CD
   |
   v
GKE
   |
   +--> Employment Management
   |
   +--> PostgreSQL
   |
   +--> Gateway API
   |
   +--> HTTPRoute
   |
   +--> TLS
   |
   v
136.110.176.193
   |
   v
cloudaiops.site
```

Final Argo CD state:

``` text
Application:
employment-management

Sync:
Synced

Health:
Healthy

Branch:
feature/helm-chart

Namespace:
stateful-demo
```

Final Gateway state:

``` text
Gateway:
employment-management-gateway

GatewayClass:
gke-l7-global-external-managed

IP:
136.110.176.193

Programmed:
True
```

Final application:

``` text
https://cloudaiops.site
```

------------------------------------------------------------------------

# 73. Recommended Day-to-Day Deployment Procedure

For a normal application release:

``` text
1. Make code changes
2. Run tests locally
3. Commit changes
4. Push to GitHub
5. GitHub Actions starts
6. Build application
7. Run tests
8. Build Docker image
9. Push image to GAR
10. Update Helm image tag
11. Commit Helm change
12. Push to feature/helm-chart
13. Argo CD detects the Git change
14. Argo CD automatically synchronizes
15. Kubernetes performs rollout
16. Verify pods
17. Verify Argo CD
18. Verify application URL
```

Verification commands:

``` bash
kubectl get pods -n stateful-demo
```

``` bash
kubectl get gateway -n stateful-demo
```

``` bash
kubectl get httproute -n stateful-demo
```

``` bash
argocd app get employment-management
```

Then open:

``` text
https://cloudaiops.site
```

------------------------------------------------------------------------

# 74. Important Principle

The final source of truth for Kubernetes deployment is Git.

``` text
Git = Desired State
Argo CD = Reconciler
GKE = Runtime
```

GitHub Actions builds and publishes the application artifact.

Argo CD deploys the desired Kubernetes state.

This gives the project a proper:

**CI + CD + GitOps architecture.**

------------------------------------------------------------------------

# 75. Project Summary for Resume

**Cloud-Native Employment Management Platform -- CI/CD & GitOps using
GitHub Actions, Argo CD, Helm and GKE**

Implemented a cloud-native Employment Management application using
Spring Boot, PostgreSQL, Docker, Google Artifact Registry and GKE. Built
CI automation using GitHub Actions for application build, testing,
containerization and image publishing. Implemented GitOps-based
continuous delivery using Helm and Argo CD with automated
synchronization to GKE. Configured GKE Gateway API, HTTPRoute, global
static IP, DNS and TLS to expose the application securely through a
custom domain.

Key technologies:

``` text
Java
Spring Boot
PostgreSQL
Docker
GitHub
GitHub Actions
Google Cloud
Google Artifact Registry
GKE
Kubernetes
Helm
Argo CD
Gateway API
HTTPRoute
Cloud DNS
TLS/HTTPS
```

------------------------------------------------------------------------

# 76. Final Project Name

**Cloud-Native Employment Management Platform -- CI/CD & GitOps using
GitHub Actions, Argo CD, Helm and GKE**

Documentation:

`Employment-Management-GitHub-Actions-ArgoCD.md`
