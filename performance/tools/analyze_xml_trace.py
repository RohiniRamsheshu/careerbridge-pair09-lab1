"""Extract sanitized assistant telemetry from a JMeter XML result file."""
import html
import json
import statistics
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return None
    return ordered[min(len(ordered) - 1, round((len(ordered) - 1) * fraction))]


def main(input_path, output_path, summary_path):
    root = ET.parse(input_path).getroot()
    records = []
    for sample in root.findall("httpSample"):
        if sample.attrib.get("lb") != "Assistant chat - bounded prompt":
            continue
        body = sample.findtext("responseData") or "{}"
        payload = json.loads(html.unescape(body))
        metrics = payload.get("metrics") or {}
        records.append({
            "trace_id": metrics.get("trace_id"),
            "elapsed_ms": int(sample.attrib.get("t", 0)),
            "success": sample.attrib.get("s") == "true",
            "answer": payload.get("answer", "")[:500],
            "model_calls": metrics.get("model_calls"),
            "tool_calls": metrics.get("tool_calls"),
            "repairs": metrics.get("repairs"),
            "prompt_tokens": metrics.get("prompt_tokens"),
            "completion_tokens": metrics.get("completion_tokens"),
            "estimated_tokens": metrics.get("estimated"),
            "context_utilization_percent": metrics.get("context_utilization_percent"),
            "model_ms": metrics.get("model_ms"),
            "tool_ms": metrics.get("tool_ms"),
            "total_ms": metrics.get("total_ms"),
            "database_ms": None,
            "queue_wait_ms": None,
        })
    elapsed = [r["elapsed_ms"] for r in records]
    summary = {
        "request_count": len(records),
        "successful_requests": sum(r["success"] for r in records),
        "failed_requests": sum(not r["success"] for r in records),
        "average_http_ms": round(statistics.mean(elapsed), 3) if elapsed else None,
        "p50_http_ms": percentile(elapsed, 0.50),
        "p95_http_ms": percentile(elapsed, 0.95),
        "p99_http_ms": percentile(elapsed, 0.99),
        "model_call_total": sum(r["model_calls"] or 0 for r in records),
        "tool_call_total": sum(r["tool_calls"] or 0 for r in records),
        "estimated_token_records": sum(bool(r["estimated_tokens"]) for r in records),
        "provider_token_records": sum(not bool(r["estimated_tokens"]) for r in records),
        "model_ms_available": any(r["model_ms"] is not None for r in records),
        "database_ms_available": False,
        "queue_wait_ms_available": False,
        "limitation": "The current API telemetry exposes model/tool timing but not per-request database or Kafka queue duration.",
    }
    Path(output_path).write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    Path(summary_path).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: analyze_xml_trace.py input.xml records.json summary.json")
    main(*sys.argv[1:])
