# Ollama evidence

Ollama is installed locally at version 0.40.16 and was reachable at `http://127.0.0.1:11434`
during the environment check. Available local models included `llama3.2:3b` and
`nomic-embed-text:latest`.

This does not prove that the CareerBridge assistant invoked Ollama. The CareerBridge backend was
not running, so no real assistant transcript, model-call count, provider token count, guardrail
transcript, or latency measurement is claimed here.

When the disposable backend is running, capture sanitized assistant responses and telemetry for
one successful real interaction and one guardrail-relevant interaction. Label provider-reported
token counts separately from estimates, include trace IDs, and never include credentials,
prompts containing secrets, or private user data.


## Batch 7 real invocation

The production assistant made a real Ollama fallback call for the ambiguous request
`I need guidance on choosing between two offers.` The sanitized record is
`performance/results/ollama-transcript-sanitized.json`:

- HTTP status: 200
- `model_calls`: 2
- Provider-reported tokens: prompt 989, completion 62, total 1,051
- Context utilization: 25.66%
- Model time: 86,915.4 ms; total time: 89,215.5 ms

This interaction is marked failed for correctness because the model returned an unsupported
generic “Offer 1” rather than an honest clarification or grounded result. It proves Ollama was
invoked, but it is not evidence of assistant correctness.

## Batch 8 live regression

After the grounding fix, the same ambiguous request was executed against the rebuilt isolated backend.
The sanitized transcript is `performance/results/ollama-batch8-sanitized.json`.

- HTTP status: 200
- Answer: the assistant stated that it could not verify matching records and would not invent jobs, events or offers.
- Provider-reported tokens: 1,049 total (989 prompt, 60 completion)
- Model calls: 2; tool calls: 1
- Model time: 74,008.6 ms; total time: 74,256.6 ms
- Status: correctness guard verified live; latency remains unresolved.
