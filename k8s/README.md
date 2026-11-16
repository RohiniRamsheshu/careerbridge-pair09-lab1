# Pair 09 Kubernetes preparation

These manifests are prepared but not applied. They define the six incremental
domain processes, the frontend, pair-prefixed service discovery, probes,
resource limits, and resume storage. The domain processes reuse the existing
Lab 1-compatible FastAPI implementation through `service_entrypoint.py`; this
is an incremental boundary, not a claim that the database has already been
split into six independent schemas.

## Local validation

```powershell
kubectl apply --dry-run=client -f k8s/namespace.yaml
kubectl apply --dry-run=client -f k8s/configmap.yaml
kubectl apply --dry-run=client -f k8s/domain-services.yaml
kubectl apply --dry-run=client -f k8s/storage-and-ingress.yaml
```

Create the runtime Secret outside Git using the commands in
`k8s/secret.example.yaml`. Replace `:local` image tags with approved ECR URIs
before deployment. Build the frontend with `-ApiUrl` set to the public API
LoadBalancer/Ingress URL because the browser cannot resolve internal Kubernetes
DNS names. No Kubernetes cluster was accessed during preparation.
