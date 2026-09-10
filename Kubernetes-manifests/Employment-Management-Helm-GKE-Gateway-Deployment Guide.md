# Employment Management — Helm, GKE Gateway API, PostgreSQL & Custom Domain Deployment

## Purpose

This document records the complete rebuild and deployment work performed for the **Employment Management** application using Helm, Kubernetes/GKE, PostgreSQL 18, GKE Gateway API, a Google Cloud global static external IP, Hostinger DNS, HTTPS with a self-signed TLS certificate, and a Spring Boot application on port `8080`.

The deployment was rebuilt from scratch after the previous infrastructure was destroyed.

---

## 1. Project and Environment Details

### GitHub Repository

`https://github.com/manjunath031984/Employment-Management`

Working branch:

`feature/helm-chart`

### Google Cloud

- Project ID: `gcp-dev-july-2026`
- GKE cluster: `k8s-postgres-lab`
- GKE location: `us-central1`
- Kubernetes namespace: `stateful-demo`

### Artifact Registry

- Repository: `employment-management`
- Application image:
  `us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management:3.0.0`

### Application

- Application: `employment-management`
- Port: `8080`
- Kubernetes Service: `employment-management-employment-management`

### PostgreSQL

- Image: `postgres:18`
- Database: `employee-managementdb`
- Username: `postgres`
- Lab password: `postgres`
- Port: `5432`
- Kubernetes Service: `employment-management-postgres`
- StatefulSet: `employment-management-postgres`
- Storage: `5Gi`
- StorageClass: `standard-rwo`

### Public Domain and Gateway

- Domain: `cloudaiops.site`
- Global static IP resource: `cloudaiops-gateway-ip`
- Global static IP: `34.160.13.80`
- GatewayClass: `gke-l7-global-external-managed`
- Gateway: `employment-management-gateway`
- HTTPRoute: `employment-management-route`
- TLS Secret: `cloudaiops-tls`

---

## 2. GKE Gateway API Enablement

Initially:

```bash
kubectl get gatewayclass
```

did not work because Gateway API resources were not available.

The Gateway API channel was checked:

```bash
gcloud container clusters describe k8s-postgres-lab \
  --location=us-central1 \
  --format="value(networkConfig.gatewayApiConfig.channel)"
```

The result was empty.

Gateway API Standard was enabled:

```bash
gcloud container clusters update k8s-postgres-lab \
  --location=us-central1 \
  --gateway-api=standard
```

After enabling it, GKE provided these GatewayClasses:

```text
NAME                               CONTROLLER                  ACCEPTED
gke-l7-global-external-managed     networking.gke.io/gateway   True
gke-l7-gxlb                        networking.gke.io/gateway   True
gke-l7-regional-external-managed   networking.gke.io/gateway   True
gke-l7-rilb                        networking.gke.io/gateway   True
```

Because the required GatewayClass is already managed by GKE, the Helm chart uses:

```yaml
gateway:
  createClass: false
```

The conditional `gatewayclass.yaml` is:

```yaml
{{- if .Values.gateway.createClass }}
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: {{ .Values.gateway.className }}
spec:
  controllerName: networking.gke.io/gateway
{{- end }}
```

---

## 3. Helm Chart Structure

Chart root:

```text
/d/Employment Management/Kubernetes-manifests
```

The chart is at the root of `Kubernetes-manifests`; it is not nested inside another chart directory.

Main structure:

```text
Kubernetes-manifests/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── statefulset.yaml
│   ├── headless-service.yaml
│   ├── postgres-configmap.yaml
│   ├── postgres-secret.yaml
│   ├── tls-secret.yaml
│   ├── gatewayclass.yaml
│   ├── gateway.yaml
│   └── httproute.yaml
└── ...
```

Once the manifests were converted into Helm templates, the raw manifest files outside `templates/` were no longer required for Helm deployment.

---

## 4. Chart.yaml

```yaml
apiVersion: v2
name: employment-management
description: A Helm chart for Employment Management application with PostgreSQL database and GKE Gateway API resources.
type: application
version: 0.1.0
appVersion: "3.0.0"
```

---

## 5. values.yaml

The deployment values were:

```yaml
nameOverride: ""
fullnameOverride: ""

app:
  replicaCount: 1
  image:
    repository: us-central1-docker.pkg.dev/gcp-dev-july-2026/employment-management/employment-management
    tag: "3.0.0"
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
  resources:
    requests:
      cpu: "100m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

gateway:
  enabled: true
  className: gke-l7-global-external-managed
  ipName: cloudaiops-gateway-ip
  tlsSecretName: cloudaiops-tls
  hostname: cloudaiops.site
  createClass: false
```

An unused `tlsPasswordBase64` value was removed/not required.

---

## 6. Helm Helpers

The `_helpers.tpl` file defines chart naming, PostgreSQL naming, common labels, and application selector labels:

```tpl
{{/*
Chart name.
*/}}
{{- define "employment-management.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified application name.
*/}}
{{- define "employment-management.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "employment-management.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
PostgreSQL resource name.
*/}}
{{- define "employment-management.postgresName" -}}
{{- printf "%s-postgres" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "employment-management.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "employment-management.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Application selector labels.
*/}}
{{- define "employment-management.selectorLabels" -}}
app.kubernetes.io/name: {{ include "employment-management.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## 7. Application Service

The application Service uses the Helm fullname and selector helpers:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "employment-management.fullname" . }}
  namespace: {{ .Release.Namespace }}
  labels:
    {{- include "employment-management.labels" . | nindent 4 }}
spec:
  type: {{ .Values.app.service.type }}
  selector:
    {{- include "employment-management.selectorLabels" . | nindent 4 }}
  ports:
    - name: http
      port: {{ .Values.app.service.port }}
      targetPort: 8080
      protocol: TCP
```

Resulting Service:

```text
employment-management-employment-management
```

Port:

```text
8080/TCP
```

Type:

```text
ClusterIP
```

---

## 8. PostgreSQL Headless Service

The PostgreSQL Service is a headless Service:

```text
ClusterIP: None
```

Service:

```text
employment-management-postgres
```

Port:

```text
5432/TCP
```

Its endpoint was:

```text
10.29.128.8:5432
```

The headless Service provides Kubernetes DNS-based access to the StatefulSet pod.

---

## 9. PostgreSQL 18 StatefulSet Storage Fix

The PostgreSQL image is:

```text
postgres:18
```

The first deployment mounted the persistent volume at:

```text
/var/lib/postgresql/data
```

PostgreSQL 18 reported a data-directory layout problem. The mount was corrected to:

```text
/var/lib/postgresql
```

The corrected mount is:

```yaml
volumeMounts:
  - name: postgres-data
    mountPath: /var/lib/postgresql
```

The StatefulSet security context uses:

```yaml
securityContext:
  fsGroup: 999
```

The PVC template uses:

```yaml
accessModes:
  - ReadWriteOnce
storageClassName: standard-rwo
resources:
  requests:
    storage: 5Gi
```

This allowed PostgreSQL 18 to initialize correctly on a fresh volume.

---

## 10. Old PVC Cleanup

After correcting the mount path, PostgreSQL still failed because the old PVC retained the previous directory layout.

The PVC was:

```text
postgres-data-employment-management-postgres-0
```

It was deleted with:

```bash
kubectl delete pvc postgres-data-employment-postgres-0 \
  -n stateful-demo
```

The PVC remained `Terminating` because the PostgreSQL StatefulSet pod was still using it.

The StatefulSet was scaled to zero:

```bash
kubectl scale statefulset employment-management-postgres \
  --replicas=0 \
  -n stateful-demo
```

After the pod disappeared, the PVC was removed.

The StatefulSet was then scaled back to one:

```bash
kubectl scale statefulset employment-management-postgres \
  --replicas=1 \
  -n stateful-demo
```

PostgreSQL became healthy:

```text
employment-management-postgres-0   1/1   Running   0 restarts
```

A fresh persistent volume was therefore created using the corrected PostgreSQL 18 directory layout.

---

## 11. Helm Validation

The chart was validated:

```bash
helm lint .
```

Result:

```text
==> Linting .
[INFO] Chart.yaml: icon is recommended
1 chart(s) linted, 0 chart(s) failed
```

The templates were rendered:

```bash
helm template employment-management . \
  --namespace stateful-demo > rendered.yaml
```

The rendered resources included:

- PostgreSQL Secret
- TLS Secret
- PostgreSQL ConfigMap
- PostgreSQL headless Service
- Application Service
- Application Deployment
- PostgreSQL StatefulSet
- Gateway
- HTTPRoute

A server-side dry run was also completed:

```bash
helm install employment-management . \
  --namespace stateful-demo \
  --create-namespace \
  --dry-run=server
```

The dry run completed successfully.

---

## 12. Helm Installation and Upgrade

Initial installation:

```bash
helm install employment-management . \
  --namespace stateful-demo \
  --create-namespace
```

Result:

```text
NAME: employment-management
NAMESPACE: stateful-demo
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
```

After the PostgreSQL storage correction, the release was upgraded:

```bash
helm upgrade employment-management . \
  --namespace stateful-demo
```

Result:

```text
Release "employment-management" has been upgraded.
STATUS: deployed
REVISION: 2
DESCRIPTION: Upgrade complete
```

---

## 13. Application Connectivity Troubleshooting

Initially the application pod entered:

```text
CrashLoopBackOff
```

Application logs showed:

```text
SQLState 08001
The connection attempt failed.
```

The root cause was:

```text
java.net.UnknownHostException: employment-management-postgres
```

The PostgreSQL Service was then checked:

```bash
kubectl get svc employment-management-postgres \
  -n stateful-demo
```

Result:

```text
NAME                             TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)
employment-management-postgres   ClusterIP   None         <none>        5432/TCP
```

The endpoint was checked:

```bash
kubectl get endpoints employment-management-postgres \
  -n stateful-demo
```

Result:

```text
NAME                             ENDPOINTS
employment-management-postgres   10.29.128.8:5432
```

This confirmed that the PostgreSQL Service existed and had a valid endpoint.

---

## 14. Kubernetes DNS Verification Without BusyBox

Rather than creating a temporary BusyBox pod, DNS was tested from the existing PostgreSQL pod.

Directly running:

```bash
kubectl exec -it employment-management-postgres-0 \
  -n stateful-demo -- cat /etc/resolv.conf
```

caused Git Bash on Windows to interpret `/etc/resolv.conf` as a local Windows path.

The working command was:

```bash
kubectl exec -it employment-management-postgres-0 \
  -n stateful-demo -- sh -c 'cat /etc/resolv.conf'
```

DNS configuration:

```text
search stateful-demo.svc.cluster.local svc.cluster.local cluster.local us-central1-b.c.gcp-dev-july-2026.internal c.gcp-dev-july-2026.internal google.internal
nameserver 34.118.224.10
options ndots:5
```

The PostgreSQL Service was then resolved from the PostgreSQL pod:

```bash
kubectl exec -it employment-management-postgres-0 \
  -n stateful-demo -- sh -c 'getent hosts employment-management-postgres'
```

Result:

```text
10.29.128.8 employment-management-postgres.stateful-demo.svc.cluster.local
```

This proved that Kubernetes DNS was functioning correctly.

The application pod subsequently reached:

```text
1/1 Running
```

and the public application became accessible.

---

## 15. Final Pod Status

The final pod status was:

```text
employment-management-employment-management-85548745b5-6dpjq   1/1   Running
employment-management-postgres-0                               1/1   Running
```

---

## 16. GKE Gateway Configuration

The Gateway uses the GKE-managed GatewayClass:

```yaml
gatewayClassName: gke-l7-global-external-managed
```

It references a named global static IP:

```yaml
addresses:
  - type: NamedAddress
    value: cloudaiops-gateway-ip
```

The listener is:

```text
Name: https
Port: 443
Protocol: HTTPS
TLS Mode: Terminate
TLS Secret: cloudaiops-tls
```

The intended hostname is:

```text
cloudaiops.site
```

Gateway:

```text
employment-management-gateway
```

---

## 17. Gateway Programming Error

Initially the Gateway showed:

```text
ADDRESS: blank
PROGRAMMED: False
```

The Gateway description identified the exact cause:

```text
Error GWCER106:
Gateway "stateful-demo/employment-management-gateway" is invalid,
err: address "cloudaiops-gateway-ip" does not exist.
```

The Helm Gateway configuration was referencing a Google Cloud global static IP resource that had not yet been created.

---

## 18. Global Static IP Creation

The missing global static IP was created:

```bash
gcloud compute addresses create cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026
```

The address was retrieved with:

```bash
gcloud compute addresses describe cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026 \
  --format="get(address)"
```

The resulting IP was:

```text
34.160.13.80
```

After GKE reconciled the Gateway, the status became:

```text
NAME                            CLASS                            ADDRESS        PROGRAMMED
employment-management-gateway   gke-l7-global-external-managed   34.160.13.80   True
```

This confirmed that the Gateway was successfully programmed.

---

## 19. Hostinger DNS Configuration

The Hostinger DNS record for the root domain was configured as:

```text
Type:    A
Name:    @
Content: 34.160.13.80
TTL:     300
```

Therefore:

```text
cloudaiops.site
        ↓
34.160.13.80
        ↓
GKE Gateway
```

If `www` access is required, the recommended record is:

```text
Type:    CNAME
Name:    www
Content: cloudaiops.site
TTL:     300
```

---

## 20. Public DNS Verification

DNS was verified with:

```bash
nslookup cloudaiops.site
```

Result:

```text
Server:  UnKnown
Address: 192.168.0.1

Non-authoritative answer:
Name:    cloudaiops.site
Address: 34.160.13.80
```

The important result is:

```text
cloudaiops.site → 34.160.13.80
```

Therefore public DNS is correctly pointing to the GKE Gateway.

---

## 21. Final Application Test

The application was opened in the browser using:

```text
https://cloudaiops.site
```

The Employment Management UI loaded successfully.

The UI showed:

```text
Employment Management
Spring Boot CRUD Practice Application
API Connected
PostgreSQL Active
```

The initial employee count was:

```text
0
```

This is expected for a newly initialized database.

The browser successfully reached the application through the public domain.

---

## 22. Final Working Architecture

```text
                         INTERNET
                            |
                            v
                  https://cloudaiops.site
                            |
                            v
                     Hostinger DNS
                            |
                            v
                     34.160.13.80
                            |
                            v
                 GKE Global Gateway
       gke-l7-global-external-managed
                            |
                            | HTTPS :443
                            v
              employment-management-gateway
                            |
                            v
             employment-management-route
                            |
                            v
        employment-management-employment-management
                         :8080
                            |
                            v
                   Spring Boot App
                            |
                            | PostgreSQL :5432
                            v
             employment-management-postgres
                            |
                            v
          employment-management-postgres-0
                            |
                            v
                 Persistent Volume
                         5Gi
```

---

## 23. Important Resource Names

### Namespace

```text
stateful-demo
```

### Application

```text
employment-management-employment-management
```

### Application Service

```text
employment-management-employment-management
```

### PostgreSQL StatefulSet

```text
employment-management-postgres
```

### PostgreSQL Service

```text
employment-management-postgres
```

### Gateway

```text
employment-management-gateway
```

### HTTPRoute

```text
employment-management-route
```

### TLS Secret

```text
cloudaiops-tls
```

### PostgreSQL Secret

```text
employment-management-postgres
```

### PostgreSQL ConfigMap

```text
employment-management-postgres
```

---

## 24. Important Commands

### Check cluster nodes

```bash
kubectl get nodes
```

### Check GatewayClasses

```bash
kubectl get gatewayclass
```

### Check Helm releases

```bash
helm list -n stateful-demo
```

### Validate Helm

```bash
helm lint .
```

### Render Helm templates

```bash
helm template employment-management . \
  --namespace stateful-demo > rendered.yaml
```

### Server-side Helm dry run

```bash
helm install employment-management . \
  --namespace stateful-demo \
  --create-namespace \
  --dry-run=server
```

### Install Helm release

```bash
helm install employment-management . \
  --namespace stateful-demo \
  --create-namespace
```

### Upgrade Helm release

```bash
helm upgrade employment-management . \
  --namespace stateful-demo
```

### Check all resources

```bash
kubectl get all -n stateful-demo
```

### Check PostgreSQL Service

```bash
kubectl get svc employment-management-postgres \
  -n stateful-demo
```

### Check PostgreSQL endpoint

```bash
kubectl get endpoints employment-management-postgres \
  -n stateful-demo
```

### Check application logs

```bash
kubectl logs deployment/employment-management-employment-management \
  -n stateful-demo
```

### Check PostgreSQL logs

```bash
kubectl logs employment-management-postgres-0 \
  -n stateful-demo
```

### Check Gateway

```bash
kubectl get gateway employment-management-gateway \
  -n stateful-demo
```

### Describe Gateway

```bash
kubectl describe gateway employment-management-gateway \
  -n stateful-demo
```

### Check Kubernetes DNS configuration

```bash
kubectl exec -it employment-management-postgres-0 \
  -n stateful-demo -- sh -c 'cat /etc/resolv.conf'
```

### Resolve PostgreSQL Service

```bash
kubectl exec -it employment-management-postgres-0 \
  -n stateful-demo -- sh -c 'getent hosts employment-management-postgres'
```

### Create global static IP

```bash
gcloud compute addresses create cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026
```

### Get global static IP

```bash
gcloud compute addresses describe cloudaiops-gateway-ip \
  --global \
  --project=gcp-dev-july-2026 \
  --format="get(address)"
```

### Test public DNS

```bash
nslookup cloudaiops.site
```

---

## 25. Troubleshooting Lessons Learned

### Lesson 1 — Enable GKE Gateway API

Gateway API Standard was required:

```bash
gcloud container clusters update k8s-postgres-lab \
  --location=us-central1 \
  --gateway-api=standard
```

### Lesson 2 — Use the GKE-managed GatewayClass

The required GatewayClass already exists:

```text
gke-l7-global-external-managed
```

Therefore:

```yaml
gateway:
  createClass: false
```

### Lesson 3 — PostgreSQL 18 storage layout

For this PostgreSQL 18 deployment, the persistent volume mount needed to be:

```text
/var/lib/postgresql
```

rather than:

```text
/var/lib/postgresql/data
```

### Lesson 4 — Old PVC data can preserve an invalid layout

The old PVC had to be removed after scaling the StatefulSet to zero so PostgreSQL could initialize a fresh volume using the corrected layout.

### Lesson 5 — Verify Service endpoints

The PostgreSQL Service had:

```text
10.29.128.8:5432
```

which confirmed that the Service selector was finding the PostgreSQL pod.

### Lesson 6 — Kubernetes DNS and public DNS are different

Hostinger resolves:

```text
cloudaiops.site
```

Kubernetes resolves:

```text
employment-management-postgres
```

Hostinger DNS cannot replace Kubernetes internal Service DNS.

### Lesson 7 — NamedAddress requires an existing GCP static IP

The Gateway initially failed because:

```text
cloudaiops-gateway-ip
```

did not exist.

Creating the global address fixed the Gateway:

```text
34.160.13.80
```

and the Gateway became:

```text
PROGRAMMED=True
```

### Lesson 8 — Point public DNS to the Gateway

The correct public flow is:

```text
cloudaiops.site
        ↓
34.160.13.80
        ↓
GKE Gateway
```

The public domain should not point directly to the internal application or PostgreSQL Service.

---

## 26. Final Status

| Component | Status |
|---|---|
| GKE cluster | Working |
| GKE Gateway API | Enabled |
| GKE GatewayClass | Available |
| Helm chart | Valid |
| Helm release | Deployed |
| PostgreSQL 18 | Running |
| PostgreSQL PVC | Working |
| PostgreSQL Service | Working |
| PostgreSQL endpoint | `10.29.128.8:5432` |
| Kubernetes DNS | Working |
| Spring Boot application | Running |
| Application Service | Working |
| Gateway | `PROGRAMMED=True` |
| Global static IP | `34.160.13.80` |
| Hostinger A record | Correct |
| Public DNS | Resolves correctly |
| Domain | `cloudaiops.site` |
| HTTPS endpoint | Reachable |
| Application UI | Loading |
| API connection | Connected |
| PostgreSQL status in UI | Active |
| Initial employee records | 0 |

---

## 27. Security Notes

This is currently a lab/practice environment.

The PostgreSQL credentials:

```text
postgres / postgres
```

should not be used in production.

The TLS certificate is self-signed. HTTPS is working, but the browser may display **Not secure** because the certificate is not issued by a browser-trusted certificate authority.

For production:

1. Use a browser-trusted TLS certificate.
2. Do not commit private TLS keys to Git.
3. Do not store production passwords directly in `values.yaml`.
4. Use Kubernetes Secrets or an external secret-management solution.
5. Rotate any private key that has been exposed during troubleshooting.
6. Use dedicated PostgreSQL credentials rather than `postgres/postgres`.
7. Use appropriate production resource sizing and security policies.

---

## 28. Final Verification

Run:

```bash
kubectl get pods -n stateful-demo
```

Expected:

```text
employment-management-employment-management-...   1/1   Running
employment-management-postgres-0                  1/1   Running
```

Check the application Service:

```bash
kubectl get svc employment-management-employment-management \
  -n stateful-demo
```

Check PostgreSQL:

```bash
kubectl get svc employment-management-postgres \
  -n stateful-demo
```

Check Gateway:

```bash
kubectl get gateway employment-management-gateway \
  -n stateful-demo
```

Expected:

```text
ADDRESS        PROGRAMMED
34.160.13.80   True
```

Check public DNS:

```bash
nslookup cloudaiops.site
```

Expected:

```text
Address: 34.160.13.80
```

Finally open:

```text
https://cloudaiops.site
```

Expected UI indicators:

```text
Employment Management
API Connected
PostgreSQL Active
```

---

## 29. Deployment Completion

The Employment Management application was successfully rebuilt and exposed publicly using:

- Helm
- Kubernetes
- GKE
- GKE Gateway API
- GKE-managed `gke-l7-global-external-managed` GatewayClass
- PostgreSQL 18
- StatefulSet and persistent storage
- Google Cloud global static IP
- Hostinger DNS
- HTTPS
- Spring Boot
- HTTPRoute

Final public endpoint:

```text
https://cloudaiops.site
```

The complete path from public DNS through the GKE Gateway, HTTPRoute, Spring Boot application, Kubernetes Service, and PostgreSQL database is operational.
