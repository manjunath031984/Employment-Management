# Employment Management GitOps — Complete Destroy Guide

## 1. Purpose

This guide explains how to completely destroy the current **Employment Management GitOps environment** that was deployed on GKE.

The environment contains:

- GKE cluster: `employment-management-gke`
- GKE region: `us-central1`
- GCP project: `gcp-dev-july-2026`
- Kubernetes namespace: `stateful-demo`
- Argo CD release: `argocd`
- Employment Management Helm release: `employment-management`
- Artifact Registry repository: `employment-management`
- Global static IP: `cloudaiops-gateway-ip`
- Static IP: `8.233.81.181`
- Public hostname: `cloudaiops.site`

> **WARNING:** These commands are destructive. PostgreSQL data stored in the Kubernetes environment will be deleted when the namespace/cluster is destroyed. Make sure anything important has been backed up before proceeding.

---

# 2. Destruction Strategy

The recommended order is:

```text
1. Set GCP project
2. Get GKE credentials
3. Delete Argo CD Application
4. Uninstall Employment Management Helm release
5. Uninstall Argo CD
6. Delete the Kubernetes namespace
7. Verify Gateway/load-balancer cleanup
8. Release the global static IP
9. Delete the GKE cluster
10. Delete Artifact Registry repository
11. Remove DNS record
12. Verify remaining GCP resources
```

The order matters because some Google Cloud resources are controller-managed and may still depend on the Gateway or cluster.

---

# 3. Set the GCP Project

Set the project used by the environment:

```bash
gcloud config set project gcp-dev-july-2026
```

Verify:

```bash
gcloud config get-value project
```

Expected:

```text
gcp-dev-july-2026
```

### Why

This prevents commands from accidentally operating against another GCP project.

---

# 4. Get Credentials for the GKE Cluster

Get credentials for the existing cluster:

```bash
gcloud container clusters get-credentials employment-management-gke \
  --region us-central1 \
  --project gcp-dev-july-2026
```

Verify connectivity:

```bash
kubectl get nodes
```

You should see the GKE worker nodes.

---

# 5. Verify the Current Environment Before Destroying

Check the namespace:

```bash
kubectl get namespace stateful-demo
```

Check Helm releases:

```bash
helm list -n stateful-demo
```

Expected releases may include:

```text
argocd
employment-management
```

Check the Argo CD Application:

```bash
kubectl get application -n stateful-demo
```

Check the Gateway:

```bash
kubectl get gateway -n stateful-demo
```

Check the HTTPRoute:

```bash
kubectl get httproute -n stateful-demo
```

Check the HealthCheckPolicies:

```bash
kubectl get healthcheckpolicies.networking.gke.io \
  -n stateful-demo
```

### Why

This gives you a final inventory before deletion and helps identify anything that was manually added.

---

# 6. Delete the Argo CD Application

The Argo CD Application is:

```text
employment-management
```

Delete it:

```bash
kubectl delete application employment-management \
  -n stateful-demo \
  --ignore-not-found
```

Verify:

```bash
kubectl get application employment-management \
  -n stateful-demo
```

Expected:

```text
Error from server (NotFound)
```

### Why

Argo CD is a GitOps controller. Removing the Application first prevents Argo CD from continuing to manage/reconcile the application while you are destroying the underlying resources.

---

# 7. Uninstall the Employment Management Helm Release

Uninstall the application Helm release:

```bash
helm uninstall employment-management \
  -n stateful-demo
```

Verify:

```bash
helm list -n stateful-demo
```

The `employment-management` release should no longer appear.

### Check remaining application resources

```bash
kubectl get all -n stateful-demo
```

Argo CD resources may still exist at this point.

### Why

This removes resources owned by the Employment Management Helm chart, including resources such as:

- Deployment
- Service
- StatefulSet
- PostgreSQL Service
- PostgreSQL StatefulSet
- Gateway
- HTTPRoute
- HealthCheckPolicy
- ServiceAccount
- RBAC resources
- ConfigMaps
- Secrets managed by the chart

---

# 8. Uninstall Argo CD

Remove the Argo CD Helm release:

```bash
helm uninstall argocd \
  -n stateful-demo
```

Verify:

```bash
helm list -n stateful-demo
```

Check the namespace:

```bash
kubectl get pods -n stateful-demo
```

Argo CD pods should begin disappearing.

### Why

Argo CD is no longer required once the GitOps-managed application has been removed.

---

# 9. Delete the Kubernetes Namespace

The namespace is:

```text
stateful-demo
```

Delete it:

```bash
kubectl delete namespace stateful-demo
```

Monitor deletion:

```bash
kubectl get namespace stateful-demo
```

Wait until:

```text
Error from server (NotFound)
```

You can also check:

```bash
kubectl get pods -A
```

### Important

Deleting the namespace removes the namespaced PostgreSQL resources and their Kubernetes objects.

This includes the PostgreSQL PVC created for this environment.

### Why

The namespace is the cleanest final Kubernetes boundary for this environment because it contains both:

- Employment Management resources
- Argo CD resources

---

# 10. Verify the Gateway Was Removed

The Gateway created a Google Cloud external load balancer.

Check Kubernetes:

```bash
kubectl get gateway -A
```

Also check Google Cloud forwarding rules:

```bash
gcloud compute forwarding-rules list \
  --global \
  --project gcp-dev-july-2026
```

Check backend services:

```bash
gcloud compute backend-services list \
  --global \
  --project gcp-dev-july-2026
```

Search specifically for the Argo CD backend:

```bash
gcloud compute backend-services list \
  --global \
  --filter="name~argocd-server"
```

Search for Employment Management backend services:

```bash
gcloud compute backend-services list \
  --global \
  --filter="name~employment-management"
```

### Why

The load balancer resources are controller-managed. They may take some time to disappear after the Gateway is deleted.

Do not manually delete generated backend services or NEGs unless you have confirmed the GKE Gateway controller is no longer managing them.

---

# 11. Release the Global Static IP

The reserved global address is:

```text
IP: 8.233.81.181
Name: cloudaiops-gateway-ip
```

First verify it:

```bash
gcloud compute addresses list \
  --global \
  --project gcp-dev-july-2026 \
  --filter="address=8.233.81.181"
```

Expected resource name:

```text
cloudaiops-gateway-ip
```

Release it:

```bash
gcloud compute addresses delete cloudaiops-gateway-ip \
  --global \
  --project gcp-dev-july-2026
```

Confirm the deletion when prompted.

Verify:

```bash
gcloud compute addresses list \
  --global \
  --project gcp-dev-july-2026 \
  --filter="address=8.233.81.181"
```

There should be no result.

### Why

A reserved static external IP is a billable/allocated Google Cloud resource. Releasing it prevents it from remaining reserved after the environment is gone.

### If deletion says the IP is still in use

The Gateway/load balancer has not finished releasing it.

Check:

```bash
gcloud compute forwarding-rules list \
  --global \
  --project gcp-dev-july-2026
```

Also verify that the Kubernetes Gateway is gone:

```bash
kubectl get gateway -A
```

Wait for the controller-managed load balancer resources to disappear, then retry:

```bash
gcloud compute addresses delete cloudaiops-gateway-ip \
  --global \
  --project gcp-dev-july-2026
```

---

# 12. Delete the GKE Cluster

Once the namespace and Gateway resources are gone, delete the cluster:

```bash
gcloud container clusters delete employment-management-gke \
  --region us-central1 \
  --project gcp-dev-july-2026
```

Confirm when prompted.

Verify:

```bash
gcloud container clusters list \
  --project gcp-dev-july-2026
```

The cluster should no longer appear.

### Why

This deletes the compute infrastructure hosting:

- Application pods
- PostgreSQL
- Argo CD
- Kubernetes control-plane association for this environment
- GKE node pools

---

# 13. Delete the Artifact Registry Repository

The repository is:

```text
employment-management
```

Location:

```text
us-central1
```

Verify:

```bash
gcloud artifacts repositories list \
  --location us-central1 \
  --project gcp-dev-july-2026
```

Delete:

```bash
gcloud artifacts repositories delete employment-management \
  --location us-central1 \
  --project gcp-dev-july-2026
```

Confirm when prompted.

Verify:

```bash
gcloud artifacts repositories list \
  --location us-central1 \
  --project gcp-dev-july-2026
```

### Why

This removes the container images used by the application, including previous image tags such as:

```text
1.0.8
1.0.9
```

and other tags stored in the repository.

---

# 14. Remove the DNS A Record

The domain used by the environment is:

```text
cloudaiops.site
```

The DNS record was:

```text
cloudaiops.site -> 8.233.81.181
```

After releasing the static IP, remove the corresponding DNS `A` record from your DNS provider.

### Why

Otherwise the DNS name will continue pointing to the old IP address even though the GCP environment has been destroyed.

---

# 15. Verify No GKE Cluster Remains

Run:

```bash
gcloud container clusters list \
  --project gcp-dev-july-2026
```

The `employment-management-gke` cluster should be absent.

---

# 16. Verify No Reserved Global IP Remains

Run:

```bash
gcloud compute addresses list \
  --global \
  --project gcp-dev-july-2026
```

The following should be absent:

```text
cloudaiops-gateway-ip
8.233.81.181
```

---

# 17. Verify Artifact Registry

Run:

```bash
gcloud artifacts repositories list \
  --location us-central1 \
  --project gcp-dev-july-2026
```

The following should be absent:

```text
employment-management
```

---

# 18. Verify Kubernetes Context

After the cluster is deleted, the current kubeconfig context may still reference the old cluster.

Check:

```bash
kubectl config current-context
```

List contexts:

```bash
kubectl config get-contexts
```

You can remove the old context after the cluster is destroyed if desired:

```bash
kubectl config delete-context gke_gcp-dev-july-2026_us-central1_employment-management-gke
```

The exact context name can be checked using:

```bash
kubectl config get-contexts
```

---

# 19. GitHub Repository Is Not Deleted

Destroying the GCP/GKE environment does **not** delete the GitHub repository.

Your repository remains:

```text
manjunath031984/Employment-Management
```

Your branch remains:

```text
feature/github-actions-ci
```

The following GitOps files also remain in GitHub:

```text
Kubernetes-manifests/
```

### Why

The destroy process removes runtime infrastructure, not source code.

You can recreate the environment later from the same repository.

---

# 20. GitHub Actions / Workload Identity Federation

Do not automatically delete these resources unless they are dedicated only to this project:

```text
github-actions-pool
github-provider
infra-admin@gcp-dev-july-2026.iam.gserviceaccount.com
```

These were used by GitHub Actions through Workload Identity Federation.

### Why

They may be reusable for future deployments.

If they are shared with other projects or workflows, deleting them could break those workflows.

---

# 21. Complete Destruction Command Summary

For a full environment destruction, the high-level command sequence is:

```bash
gcloud config set project gcp-dev-july-2026
```

```bash
gcloud container clusters get-credentials employment-management-gke \
  --region us-central1 \
  --project gcp-dev-july-2026
```

```bash
kubectl delete application employment-management \
  -n stateful-demo \
  --ignore-not-found
```

```bash
helm uninstall employment-management \
  -n stateful-demo
```

```bash
helm uninstall argocd \
  -n stateful-demo
```

```bash
kubectl delete namespace stateful-demo
```

Wait for Gateway/load-balancer cleanup, then:

```bash
gcloud compute addresses delete cloudaiops-gateway-ip \
  --global \
  --project gcp-dev-july-2026
```

Then:

```bash
gcloud container clusters delete employment-management-gke \
  --region us-central1 \
  --project gcp-dev-july-2026
```

Then:

```bash
gcloud artifacts repositories delete employment-management \
  --location us-central1 \
  --project gcp-dev-july-2026
```

Finally, remove the DNS A record:

```text
cloudaiops.site -> 8.233.81.181
```

---

# 22. Final Verification Checklist

After destruction, verify:

```text
[ ] Argo CD Application deleted
[ ] Employment Management Helm release deleted
[ ] Argo CD Helm release deleted
[ ] stateful-demo namespace deleted
[ ] Gateway deleted
[ ] HTTPRoute deleted
[ ] HealthCheckPolicy deleted
[ ] Global load balancer cleaned up
[ ] Static IP 8.233.81.181 released
[ ] cloudaiops-gateway-ip released
[ ] GKE cluster employment-management-gke deleted
[ ] Artifact Registry employment-management deleted
[ ] DNS A record removed
[ ] GitHub repository retained
[ ] GitHub Actions/WIF resources reviewed before deletion
```

---

# 23. Important: What Is Preserved

The following are **not deleted by this guide**:

- GitHub repository
- Git history
- `feature/github-actions-ci`
- Source code
- Helm templates
- Kubernetes manifests stored in Git
- GitHub Actions workflow definitions
- WIF resources unless you explicitly remove them
- Your DNS domain itself

This allows the environment to be recreated later from the GitHub repository.
