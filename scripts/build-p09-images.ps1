param(
  [string]$Registry = "p09-careerbridge",
  [string]$Tag = "local",
  [string]$ApiUrl = "http://localhost:9090"
)

$ErrorActionPreference = "Stop"
$services = @(
  @{ Name = "backend"; Context = "backend"; Dockerfile = "Dockerfile" },
  @{ Name = "student"; Context = "backend"; Dockerfile = "Dockerfile.student" },
  @{ Name = "company"; Context = "backend"; Dockerfile = "Dockerfile.company" },
  @{ Name = "job"; Context = "backend"; Dockerfile = "Dockerfile.job" },
  @{ Name = "application"; Context = "backend"; Dockerfile = "Dockerfile.application" },
  @{ Name = "event"; Context = "backend"; Dockerfile = "Dockerfile.event" },
  @{ Name = "assistant"; Context = "backend"; Dockerfile = "Dockerfile.assistant" },
  @{ Name = "frontend"; Context = "frontend"; Dockerfile = "Dockerfile" }
)

foreach ($service in $services) {
  if ($service.Name -eq "frontend") {
    docker build --build-arg "VITE_API_URL=$ApiUrl" -t "$Registry/$($service.Name):$Tag" -f "$($service.Context)/$($service.Dockerfile)" $service.Context
  } else {
    docker build -t "$Registry/$($service.Name):$Tag" -f "$($service.Context)/$($service.Dockerfile)" $service.Context
  }
}
