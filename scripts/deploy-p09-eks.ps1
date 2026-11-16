param(
  [Parameter(Mandatory = $true)][string]$Namespace,
  [Parameter(Mandatory = $true)][string]$ImageRegistry
)

$ErrorActionPreference = "Stop"
if ($Namespace -ne "p09-careerbridge") { throw "Refusing unexpected namespace: $Namespace" }
if ([string]::IsNullOrWhiteSpace($ImageRegistry)) { throw "ImageRegistry is required" }

Write-Host "Validation only: this script does not create AWS resources."
kubectl version --client
kubectl apply --dry-run=client -f k8s/namespace.yaml
kubectl apply --dry-run=client -f k8s/configmap.yaml
kubectl apply --dry-run=client -f k8s/api-and-workers.yaml
kubectl apply --dry-run=client -f k8s/domain-services.yaml
kubectl apply --dry-run=client -f k8s/storage-and-ingress.yaml
Write-Host "Build/push images to $ImageRegistry, create the runtime Secret, then apply these manifests only after AWS review."
