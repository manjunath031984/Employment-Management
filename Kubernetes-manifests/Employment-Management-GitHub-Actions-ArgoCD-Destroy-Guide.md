# Employment Management -- Complete Destroy Guide

## Cloud-Native Employment Management Platform

**Technology Stack:** GitHub Actions, Argo CD, Helm, Kubernetes, GKE,
Gateway API, PostgreSQL, Artifact Registry, Cloud DNS/Hostinger DNS

**Project:** `Employment Management`

**GCP Project ID:** `gcp-dev-july-2026`

**GKE Cluster:** `employment-management-gke`

**GKE Region:** `us-central1`

**Kubernetes Namespace:** `stateful-demo`

**Argo CD Application:** `employment-management`

**Git Repository:**
`https://github.com/manjunath031984/Employment-Management.git`

**Git Branch:** `feature/helm-chart`

**GitOps Path:** `Kubernetes-manifests`

**Domain:** `cloudaiops.site`

**Gateway Class:** `gke-l7-global-external-managed`

------------------------------------------------------------------------

# 1. Purpose

This guide documents the complete and safe destruction procedure for the
Employment Management platform.

The platform was deployed using:

-   GitHub Actions for CI/CD
-   GitHub repository for source control
-   Helm for Kubernetes packaging
-   Argo CD for GitOps deployment
-   Google Kubernetes Engine (GKE)
-   Kubernetes Gateway API
-   Google Cloud global external Gateway
-   Global static IP
-   Artifact Registry
-   PostgreSQL running as a Kubernetes StatefulSet
-   Persistent Volume Claim (PVC)
-   Hostinger DNS for the application domain

The objective of this guide is to remove the deployed infrastructure and
application resources without leaving unnecessary cloud resources
behind.

------------------------------------------------------------------------

# 2. Important Destruction Rules

Before starting, remember:

1.  Destroy the Argo CD application before deleting the GKE cluster.
2.  Allow Argo CD to prune Kubernetes resources.
3.  Verify that application resources are removed.
4.  Verify that the PostgreSQL PVC is removed.
5.  Delete the GKE cluster.
6.  Delete the Google Cloud static IP.
7.  Delete the Artifact Registry repository.
8.  Remove the DNS A record from Hostinger.
9.  Remove stale local Kubernetes context if required.
10. Do not delete unrelated resources from the GCP project.

> WARNING: These operations are destructive. Deleted Kubernetes
> workloads, persistent storage, container images, GKE clusters, static
> IPs, and DNS records may not be recoverable.

------------------------------------------------------------------------

# 3. Pre-Destruction Verification

## 3.1 Verify the active GCP project

``` bash
gcloud config get-value project
```

Expected:

``` text
gcp-dev-july-2026
```

If required:

``` bash
gcloud config set project gcp-dev-july-2026
```

Verify:

``` bash
gcloud projects describe gcp-dev-july-2026
```

------------------------------------------------------------------------

# 4. Verify the GKE Cluster

List clusters:

``` bash
gcloud container clusters list \
  --project=gcp-dev-july-2026
```

Expected cluster:

``` text
employment-management-gke
```

Describe the cluster if it still exists:

``` bash
gcloud container clusters describe employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026
```

------------------------------------------------------------------------

# 5. Verify kubectl Context

Check the current context:

``` bash
kubectl config current-context
```

Expected before destruction:

``` text
gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

List all contexts:

``` bash
kubectl config get-contexts
```

Make sure kubectl is pointing to the Employment Management GKE cluster
before executing Kubernetes deletion commands.

------------------------------------------------------------------------

# 6. Verify the Kubernetes Namespace

Check the namespace:

``` bash
kubectl get namespace stateful-demo
```

Expected:

``` text
NAME            STATUS
stateful-demo   Active
```

List all resources:

``` bash
kubectl get all -n stateful-demo
```

Also check:

``` bash
kubectl get gateway -n stateful-demo
kubectl get httproute -n stateful-demo
kubectl get secret -n stateful-demo
kubectl get configmap -n stateful-demo
kubectl get pvc -n stateful-demo
```

------------------------------------------------------------------------

# 7. Verify PostgreSQL Storage Before Destroying

Check PVCs:

``` bash
kubectl get pvc -n stateful-demo
```

The PostgreSQL PVC used by this project was:

``` text
postgres-data-employment-management-postgres-0
```

Check the PVC:

``` bash
kubectl describe pvc postgres-data-employment-management-postgres-0 \
  -n stateful-demo
```

Important:

The PostgreSQL PVC contains application data. If the data is required,
back it up before destruction.

------------------------------------------------------------------------

# 8. Verify Argo CD

Check Argo CD applications:

``` bash
argocd app list
```

Expected application:

``` text
employment-management
```

Get detailed status:

``` bash
argocd app get employment-management
```

A healthy application before destruction should show resources such as:

-   Deployment
-   StatefulSet
-   Services
-   Gateway
-   HTTPRoute
-   ConfigMap
-   Secrets

------------------------------------------------------------------------

# 9. Verify Argo CD Sync Policy

Check:

``` bash
argocd app get employment-management
```

The application used:

``` text
Sync Policy: Automated (Prune)
```

This is important because Argo CD can prune resources that belong to the
application.

------------------------------------------------------------------------

# 10. Destroy the Application Through Argo CD

## 10.1 Recommended method

Use Argo CD to delete the application with cascading deletion.

Run:

``` bash
argocd app delete employment-management \
  --cascade
```

Argo CD will ask for confirmation.

Enter:

``` text
y
```

If the CLI version requires explicit confirmation, use:

``` bash
argocd app delete employment-management \
  --cascade \
  --yes
```

> Use the command supported by your installed Argo CD CLI version. The
> important part is `--cascade`, which removes the resources managed by
> the application.

------------------------------------------------------------------------

# 11. Alternative: Delete From Argo CD Web UI

If using the Argo CD web UI:

1.  Open Argo CD.
2.  Go to **Applications**.
3.  Select: `employment-management`
4.  Click **DELETE**.
5.  Confirm deletion.
6.  Ensure cascading/pruning is enabled.
7.  Confirm the deletion.
8.  Wait for the application to disappear.

Do not delete the GKE cluster yet.

------------------------------------------------------------------------

# 12. Verify Argo CD Application Was Deleted

Run:

``` bash
argocd app list
```

Expected:

``` text
NAME  CLUSTER  NAMESPACE  PROJECT  STATUS  HEALTH  SYNCPOLICY  CONDITIONS  REPO  PATH  TARGET
```

with no `employment-management` application.

You can also run:

``` bash
argocd app get employment-management
```

Expected result should indicate that the application does not exist.

------------------------------------------------------------------------

# 13. Verify Kubernetes Resources Were Removed

Run all of the following:

``` bash
kubectl get pods -n stateful-demo
```

``` bash
kubectl get svc -n stateful-demo
```

``` bash
kubectl get deployment -n stateful-demo
```

``` bash
kubectl get statefulset -n stateful-demo
```

``` bash
kubectl get gateway -n stateful-demo
```

``` bash
kubectl get httproute -n stateful-demo
```

``` bash
kubectl get secret -n stateful-demo
```

``` bash
kubectl get configmap -n stateful-demo
```

``` bash
kubectl get pvc -n stateful-demo
```

Expected application resources:

``` text
No resources found in stateful-demo namespace.
```

The Kubernetes-generated `kube-root-ca.crt` ConfigMap may remain while
the namespace exists. It is a Kubernetes system resource, not an
Employment Management application resource.

------------------------------------------------------------------------

# 14. Verify the Gateway Was Removed

Run:

``` bash
kubectl get gateway -n stateful-demo
```

Expected:

``` text
No resources found in stateful-demo namespace.
```

Also:

``` bash
kubectl get httproute -n stateful-demo
```

Expected:

``` text
No resources found in stateful-demo namespace.
```

------------------------------------------------------------------------

# 15. Verify the PostgreSQL PVC Was Removed

Run:

``` bash
kubectl get pvc -n stateful-demo
```

Expected:

``` text
No resources found in stateful-demo namespace.
```

If the PVC still exists, do not proceed blindly.

Check:

``` bash
kubectl describe pvc postgres-data-employment-management-postgres-0 \
  -n stateful-demo
```

If the PVC is intentionally no longer needed and Argo CD has already
been deleted, it can be deleted manually:

``` bash
kubectl delete pvc postgres-data-employment-management-postgres-0 \
  -n stateful-demo
```

Then verify:

``` bash
kubectl get pvc -n stateful-demo
```

------------------------------------------------------------------------

# 16. Optional: Delete the Kubernetes Namespace

If `stateful-demo` is used only by Employment Management and is no
longer required:

``` bash
kubectl delete namespace stateful-demo
```

Wait for deletion:

``` bash
kubectl get namespace stateful-demo
```

Expected:

``` text
Error from server (NotFound): namespaces "stateful-demo" not found
```

Do not delete the namespace if another application uses it.

------------------------------------------------------------------------

# 17. Verify the GKE Cluster Before Deletion

Run:

``` bash
gcloud container clusters list \
  --project=gcp-dev-july-2026
```

Verify that the cluster is:

``` text
employment-management-gke
```

Region:

``` text
us-central1
```

------------------------------------------------------------------------

# 18. Delete the GKE Cluster

Only perform this after the Argo CD application and Kubernetes resources
have been destroyed.

Run:

``` bash
gcloud container clusters delete employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026
```

You will see a confirmation message similar to:

``` text
The following clusters will be deleted.

- [employment-management-gke] in [us-central1]

Do you want to continue (Y/n)?
```

Enter:

``` text
y
```

Wait until Google Cloud reports:

``` text
Deleting cluster employment-management-gke...done.
```

------------------------------------------------------------------------

# 19. Verify the GKE Cluster Was Deleted

Run:

``` bash
gcloud container clusters list \
  --project=gcp-dev-july-2026 \
  --region=us-central1
```

The cluster should no longer appear.

You can also run:

``` bash
gcloud container clusters describe employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026
```

Expected result:

``` text
NOT_FOUND
```

------------------------------------------------------------------------

# 20. Clean Up the Local kubectl Context

After the GKE cluster is deleted, the local kubeconfig may still contain
its old context.

List contexts:

``` bash
kubectl config get-contexts
```

If the old context exists:

``` bash
kubectl config delete-context gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

You can also check clusters stored in kubeconfig:

``` bash
kubectl config get-clusters
```

If the old cluster entry remains, remove it:

``` bash
kubectl config delete-cluster gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

Only remove the local entry if you no longer need it.

------------------------------------------------------------------------

# 21. Delete the Global Static IP

## 21.1 List global IP addresses

Run:

``` bash
gcloud compute addresses list \
  --global \
  --project=gcp-dev-july-2026
```

The project previously used these IP resources during deployment:

``` text
employment-management-ip
cloudaiops-gateway-ip
```

The final Gateway IP used by the application was:

``` text
cloudaiops-gateway-ip
```

Its previous address was:

``` text
136.110.176.193
```

------------------------------------------------------------------------

# 22. Delete `cloudaiops-gateway-ip`

If it still exists:

``` bash
gcloud compute addresses delete cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026
```

Confirm:

``` text
y
```

------------------------------------------------------------------------

# 23. Verify Global Static IP Cleanup

Run:

``` bash
gcloud compute addresses list \
  --global \
  --project=gcp-dev-july-2026
```

Expected:

``` text
Listed 0 items.
```

If other unrelated global addresses are listed, do not delete them
without verifying ownership.

------------------------------------------------------------------------

# 24. Delete Old `employment-management-ip` If It Still Exists

Check:

``` bash
gcloud compute addresses list \
  --global \
  --project=gcp-dev-july-2026
```

If `employment-management-ip` still exists:

``` bash
gcloud compute addresses delete employment-management-ip \
  --global \
  --project=gcp-dev-july-2026
```

Confirm:

``` text
y
```

Verify again:

``` bash
gcloud compute addresses list \
  --global \
  --project=gcp-dev-july-2026
```

------------------------------------------------------------------------

# 25. Artifact Registry Cleanup

## 25.1 List Artifact Registry repositories

Run:

``` bash
gcloud artifacts repositories list \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

The Employment Management repository was:

``` text
employment-management
```

Format:

``` text
DOCKER
```

------------------------------------------------------------------------

# 26. Delete the Artifact Registry Repository

If the repository is no longer needed:

``` bash
gcloud artifacts repositories delete employment-management \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

Confirm:

``` text
y
```

Wait for the operation to complete.

------------------------------------------------------------------------

# 27. Verify Artifact Registry Cleanup

Run:

``` bash
gcloud artifacts repositories list \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

The `employment-management` repository should no longer appear.

If no repositories are required in this location, the result may show no
repositories.

------------------------------------------------------------------------

# 28. DNS Cleanup

The application domain was:

``` text
cloudaiops.site
```

The DNS was managed through Hostinger.

During deployment, the application used a global static IP.

The old DNS record shown in Hostinger was:

``` text
Type:  A
Name:  @
Value: 34.36.234.203
TTL:   300
```

This IP belonged to the old:

``` text
employment-management-ip
```

The newer Gateway IP was:

``` text
136.110.176.193
```

This belonged to:

``` text
cloudaiops-gateway-ip
```

Both cloud IP resources were removed during final cleanup.

------------------------------------------------------------------------

# 29. Remove the Hostinger A Record

Open the Hostinger DNS management page for:

``` text
cloudaiops.site
```

Navigate to:

``` text
Domains
→ cloudaiops.site
→ DNS / Nameservers
→ DNS Records
```

Find the application A record:

``` text
Type: A
Name: @
Value: 34.36.234.203
```

Delete that record.

Do not add the old IP again.

Do not add:

``` text
136.110.176.193
```

because the corresponding Google Cloud static IP has been deleted.

------------------------------------------------------------------------

# 30. Do Not Click "Reset DNS Records"

Hostinger may provide:

``` text
Reset DNS records
```

Do not use this option for normal application cleanup.

Delete only the specific application DNS record.

This avoids accidentally removing unrelated DNS records such as:

-   Email records
-   MX records
-   SPF records
-   DKIM records
-   Verification records
-   Other websites/subdomains

------------------------------------------------------------------------

# 31. DNS Verification

After deleting the A record, DNS propagation may take some time.

From Git Bash or PowerShell, you can check DNS resolution:

``` bash
nslookup cloudaiops.site
```

Or:

``` bash
nslookup cloudaiops.site 8.8.8.8
```

The old GKE IP should no longer be returned after DNS propagation.

You can also use:

``` bash
dig cloudaiops.site
```

if `dig` is installed.

------------------------------------------------------------------------

# 32. GitHub Actions Cleanup

The GitHub repository remains source code unless you intentionally
delete it.

Repository:

``` text
https://github.com/manjunath031984/Employment-Management.git
```

Do not delete the repository if you want to retain:

-   Source code
-   GitHub Actions workflows
-   Helm chart
-   Kubernetes manifests
-   Documentation
-   Git history
-   Destroy guide

The following files may remain intentionally:

``` text
.github/workflows/ci.yaml
Kubernetes-manifests/
ai-infrastructure-agent/
```

The infrastructure destruction does not require deleting the GitHub
repository.

------------------------------------------------------------------------

# 33. GitHub Actions Secrets

Review repository secrets if the project will no longer be used.

Navigate to:

``` text
GitHub
→ Repository
→ Settings
→ Secrets and variables
→ Actions
```

Review secrets such as:

-   GCP credentials
-   Service account credentials
-   Artifact Registry credentials
-   Deployment credentials
-   Other cloud credentials

Remove credentials only if they are no longer used anywhere else.

> IMPORTANT: Never delete a credential that is shared with another
> active project without checking its usage first.

------------------------------------------------------------------------

# 34. Google Service Account Cleanup

The project used an existing Google service account:

``` text
infra-admin@gcp-dev-july-2026.iam.gserviceaccount.com
```

The service account was used for infrastructure-related operations.

Do not automatically delete this service account just because the
Employment Management environment was destroyed.

First determine whether it is used by:

-   Terraform
-   Jenkins
-   GitHub Actions
-   Other GCP projects
-   Other infrastructure
-   Workload Identity Federation
-   Other deployments

Only delete the service account if you have confirmed it is no longer
required anywhere.

------------------------------------------------------------------------

# 35. Workload Identity Federation / Identity Cleanup

If Workload Identity Federation was configured for CI/CD, review:

``` text
IAM & Admin
→ Workload Identity Federation
```

Check for providers and pools created specifically for this project.

If a pool/provider is exclusively used by the destroyed Employment
Management deployment, it can be removed after verifying that no other
workload depends on it.

Do not delete shared identity infrastructure.

------------------------------------------------------------------------

# 36. Argo CD Cluster Registration Cleanup

The GKE cluster was registered with Argo CD using:

``` bash
argocd cluster add gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

This created an Argo CD manager service account in the target cluster.

The target cluster has now been deleted.

Check Argo CD cluster registrations:

``` bash
argocd cluster list
```

If the deleted GKE cluster still appears, remove its stale Argo CD
registration.

First identify the exact server/context:

``` bash
argocd cluster list
```

Then remove the stale registration using the appropriate Argo CD CLI
command for your installed version.

Do not remove:

``` text
in-cluster
```

unless you are intentionally destroying the Argo CD installation itself.

------------------------------------------------------------------------

# 37. Argo CD Installation Cleanup

If Argo CD itself is running on Docker Desktop or another separate
Kubernetes cluster and you want to remove Argo CD completely, that is a
separate operation.

Do not remove Argo CD just because the Employment Management application
was destroyed.

If Argo CD is no longer required at all, verify where it is running
first:

``` bash
kubectl config current-context
```

Then:

``` bash
kubectl get namespaces
```

If the current cluster is Docker Desktop and Argo CD is installed in:

``` text
argocd
```

you can remove the Argo CD installation separately.

Do not run this section if Argo CD will be used for another project.

------------------------------------------------------------------------

# 38. Final Kubernetes Verification

After the GKE cluster is deleted, commands such as:

``` bash
kubectl get pods
```

against the old GKE context will fail because the cluster no longer
exists.

This is expected.

The important verification must be completed before deleting the GKE
cluster.

------------------------------------------------------------------------

# 39. Final GCP Verification

## 39.1 GKE

``` bash
gcloud container clusters list \
  --project=gcp-dev-july-2026
```

Confirm:

``` text
employment-management-gke
```

is absent.

------------------------------------------------------------------------

## 39.2 Global static IP

``` bash
gcloud compute addresses list \
  --global \
  --project=gcp-dev-july-2026
```

Confirm the application IPs are absent.

------------------------------------------------------------------------

## 39.3 Artifact Registry

``` bash
gcloud artifacts repositories list \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

Confirm:

``` text
employment-management
```

is absent.

------------------------------------------------------------------------

# 40. Final Argo CD Verification

Run:

``` bash
argocd app list
```

Expected:

``` text
NAME  CLUSTER  NAMESPACE  PROJECT  STATUS  HEALTH  SYNCPOLICY  CONDITIONS  REPO  PATH  TARGET
```

No:

``` text
employment-management
```

application should remain.

------------------------------------------------------------------------

# 41. Final DNS Verification

Check:

``` bash
nslookup cloudaiops.site
```

The old application IPs should no longer be returned after DNS
propagation.

Also verify in Hostinger:

``` text
cloudaiops.site
→ DNS / Nameservers
→ DNS Records
```

Confirm the application A record has been removed.

------------------------------------------------------------------------

# 42. Complete Destruction Checklist

Use this checklist before considering the environment completely
destroyed.

## Argo CD

-   [x] Argo CD application `employment-management` deleted
-   [x] Cascading deletion/pruning completed
-   [x] `argocd app list` no longer shows the application

## Kubernetes

-   [x] Deployment deleted
-   [x] ReplicaSet deleted
-   [x] Application pod deleted
-   [x] PostgreSQL StatefulSet deleted
-   [x] PostgreSQL pod deleted
-   [x] Application Service deleted
-   [x] PostgreSQL Service deleted
-   [x] Gateway deleted
-   [x] HTTPRoute deleted
-   [x] Application ConfigMap deleted
-   [x] Application Secrets deleted
-   [x] PostgreSQL PVC deleted
-   [x] Optional `stateful-demo` namespace deleted

## GKE

-   [x] `employment-management-gke` cluster deleted
-   [x] Cluster no longer appears in GKE list
-   [x] Local kubeconfig cleaned if required

## Google Cloud Networking

-   [x] `cloudaiops-gateway-ip` deleted
-   [x] `employment-management-ip` deleted
-   [x] No unused application global static IP remains

## Artifact Registry

-   [x] `employment-management` repository deleted
-   [x] Container images removed with the repository

## DNS

-   [x] Hostinger A record `@ → 34.36.234.203` removed
-   [x] No DNS record points to a deleted application IP
-   [x] Unrelated DNS records preserved

## CI/CD

-   [ ] GitHub Actions secrets reviewed
-   [ ] Unused CI/CD credentials removed if applicable
-   [ ] GitHub repository retained if source code/documentation is
    required

## IAM

-   [ ] `infra-admin@gcp-dev-july-2026.iam.gserviceaccount.com` reviewed
-   [ ] Shared service account not deleted accidentally
-   [ ] Unused Workload Identity Federation resources reviewed
-   [ ] Shared IAM resources preserved

------------------------------------------------------------------------

# 43. Exact Destruction Sequence Used for This Project

The final destruction sequence should be:

``` text
1. Verify GCP project
        ↓
2. Verify GKE context
        ↓
3. Verify Argo CD application
        ↓
4. Delete Argo CD application with cascade
        ↓
5. Verify Kubernetes resources are deleted
        ↓
6. Verify Gateway and HTTPRoute are deleted
        ↓
7. Verify PostgreSQL StatefulSet is deleted
        ↓
8. Verify PostgreSQL PVC is deleted
        ↓
9. Delete stateful-demo namespace if no longer required
        ↓
10. Delete GKE cluster
        ↓
11. Verify GKE cluster is gone
        ↓
12. Delete stale kubectl context if required
        ↓
13. Delete cloudaiops-gateway-ip
        ↓
14. Delete employment-management-ip if present
        ↓
15. Delete Artifact Registry employment-management repository
        ↓
16. Remove Hostinger DNS A record
        ↓
17. Verify DNS propagation
        ↓
18. Review GitHub Actions secrets
        ↓
19. Review service accounts / WIF
        ↓
20. Final GCP + Argo CD verification
```

------------------------------------------------------------------------

# 44. Resources Destroyed in the Completed Environment

The Employment Management environment used:

``` text
GCP Project
└── gcp-dev-july-2026
    │
    ├── GKE
    │   └── employment-management-gke
    │       └── stateful-demo
    │           ├── Deployment
    │           ├── Pod
    │           ├── StatefulSet
    │           ├── PostgreSQL Pod
    │           ├── Services
    │           ├── Gateway
    │           ├── HTTPRoute
    │           ├── ConfigMaps
    │           ├── Secrets
    │           └── PVC
    │
    ├── Global Static IP
    │   ├── employment-management-ip
    │   └── cloudaiops-gateway-ip
    │
    └── Artifact Registry
        └── employment-management
```

The GitOps layer was:

``` text
GitHub
└── Employment-Management
    └── feature/helm-chart
        └── Kubernetes-manifests
                ↓
             Argo CD
                ↓
             GKE
```

The CI/CD layer was:

``` text
GitHub Push
     ↓
GitHub Actions
     ↓
Build / Test
     ↓
Docker Image
     ↓
Artifact Registry
     ↓
Helm / Kubernetes manifests
     ↓
Argo CD
     ↓
GKE
```

------------------------------------------------------------------------

# 45. Important Lessons

## Never delete GKE first

If Argo CD is still managing the application, deleting GKE first can
leave stale Argo CD registrations and makes resource verification
harder.

Preferred order:

``` text
Argo CD Application
        ↓
Kubernetes resources
        ↓
GKE
        ↓
Cloud resources
```

## Always verify PVCs

PostgreSQL was deployed using a StatefulSet and PVC.

Deleting the StatefulSet does not always mean that persistent storage
has been removed.

Always run:

``` bash
kubectl get pvc -n stateful-demo
```

before considering Kubernetes cleanup complete.

## Static IP and DNS are different

Deleting a Google Cloud static IP does not automatically remove the DNS
record at Hostinger.

The DNS record must be removed separately.

## Do not delete shared IAM resources blindly

The service account:

``` text
infra-admin@gcp-dev-july-2026.iam.gserviceaccount.com
```

may be used by other infrastructure.

Review its usage before deletion.

------------------------------------------------------------------------

# 46. One-Page Quick Destroy Commands

For an already verified environment, the core destruction commands are:

## Argo CD

``` bash
argocd app get employment-management
```

``` bash
argocd app delete employment-management --cascade
```

``` bash
argocd app list
```

## Kubernetes verification

``` bash
kubectl get all -n stateful-demo
kubectl get gateway -n stateful-demo
kubectl get httproute -n stateful-demo
kubectl get pvc -n stateful-demo
```

## Optional namespace deletion

``` bash
kubectl delete namespace stateful-demo
```

## GKE

``` bash
gcloud container clusters delete employment-management-gke \
  --region=us-central1 \
  --project=gcp-dev-july-2026
```

## Static IP

``` bash
gcloud compute addresses delete cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026
```

## Artifact Registry

``` bash
gcloud artifacts repositories delete employment-management \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

## Verification

``` bash
gcloud container clusters list \
  --project=gcp-dev-july-2026
```

``` bash
gcloud compute addresses list \
  --global \
  --project=gcp-dev-july-2026
```

``` bash
gcloud artifacts repositories list \
  --location=us-central1 \
  --project=gcp-dev-july-2026
```

``` bash
argocd app list
```

------------------------------------------------------------------------

# 47. Final Status

For the completed Employment Management deployment, the following
cleanup was successfully performed:

``` text
Argo CD Application                 → Deleted
Kubernetes workloads               → Deleted
PostgreSQL StatefulSet             → Deleted
PostgreSQL PVC                     → Deleted
Gateway                            → Deleted
HTTPRoute                          → Deleted
stateful-demo application resources → Deleted
GKE employment-management-gke      → Deleted
Global static IPs                  → Deleted
Artifact Registry repository       → Deleted
```

The Hostinger DNS application A record should also be removed:

``` text
@ → 34.36.234.203
```

Do not recreate the deleted application IP.

------------------------------------------------------------------------

# 48. Final Safety Reminder

Before running any destructive command against a shared GCP project:

``` bash
gcloud config get-value project
```

Confirm:

``` text
gcp-dev-july-2026
```

Before deleting any resource, verify its name and ownership.

Never delete resources from another project or another application
simply because they have a similar name.

**End of Destroy Guide**
