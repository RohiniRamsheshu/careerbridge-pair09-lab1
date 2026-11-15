from backend.app.context_management import ContextMetrics, compact_conversation


def test_compaction_reduces_working_context_and_preserves_recent_request():
    messages = [{"role": "system", "content": "policy"}]
    messages.extend({"role": "user", "content": "important historical preference " * 30} for _ in range(8))
    messages.append({"role": "user", "content": "current request"})

    compacted, result = compact_conversation(messages, threshold=100, keep_recent=2)

    assert result["compacted"] is True
    assert result["after_tokens"] < result["before_tokens"]
    assert compacted[-1]["content"] == "current request"
    assert any(item.get("compacted") for item in compacted)


def test_token_metrics_mark_estimates_and_warn_above_seventy_percent():
    metrics = ContextMetrics(prompt_tokens=3000, completion_tokens=100, estimated=True)

    result = metrics.as_dict(context_window=4096)

    assert result["estimated"] is True
    assert result["warning"] is True
    assert result["context_utilization_percent"] > 70
