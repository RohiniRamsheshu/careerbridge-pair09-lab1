# Performance analysis

No benchmark results are recorded yet. This is intentional: JMeter is unavailable, Docker is
not accessible from the current shell, and the backend is not running. No bottleneck is claimed.

After execution, compare CRUD and assistant results using actual JTL and trace data. Analyze
database duration, outbox/Kafka wait, tool duration, Ollama inference, CPU/memory pressure,
worker capacity, connection pools, queueing, and errors separately. HTTP latency alone cannot
identify the first bottleneck.

## Measured Batch 7 analysis

CRUD remained HTTP-successful at every required level, but average latency rose from 24.8s at
100 users to 70.9s at 500 users; p99 rose from 64.9s to 175.8s. A separate health request timed
out during the 100-user run, and backend CPU reached approximately 169% in a read-only Docker
stats sample. This supports backend worker/CPU saturation and queueing as the first observed
CRUD bottleneck, but does not isolate database versus application CPU time.

Assistant chat used a deterministic search prompt, so those runs measured the production
assistant/tool path with `model_calls=0`; they are not Ollama-inference latency measurements.
The separate ambiguous request invoked Ollama and took approximately 89.2s, with model time
approximately 86.9s. Model inference is the first measured bottleneck for that fallback case.

The required graph is average CRUD response time versus concurrency. Generate it only from the
five actual CRUD summaries and retain the source CSV/JSON next to the graph. Add a separate
assistant p50/p95/p99 and error-rate comparison for 5/10/20/50 users.

