# Assistant context management

`backend/app/context_management.py` provides bounded token accounting and
compaction. Provider-reported Ollama counts are preferred; otherwise estimates are
marked as estimates. The default context window is 4096 and the default compaction
threshold is 3000 tokens, configurable with `ASSISTANT_CONTEXT_THRESHOLD` and
`ASSISTANT_CONTEXT_WINDOW`.

When the threshold is exceeded, the system message, a bounded summary of old
messages, and the latest messages are retained. The summary is explicitly history,
not authority. The original Mongo conversation remains auditable because the
repository stores the bounded conversation record; compaction only changes the
working request context. A compaction marker prevents an unbounded compaction loop.

`/memory` remains the inspection command for durable student memory. Memory and
conversation records are scoped by authenticated student ID.

No real model token counts or recall-after-compaction transcript were captured in
this batch. The deterministic accounting and compaction behavior require the
focused backend tests; real Ollama evidence remains outstanding.
