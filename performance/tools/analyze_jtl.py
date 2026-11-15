"""Summarize actual JMeter JTL samples without inventing component timings."""
import csv
import json
import statistics
import sys
from pathlib import Path


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def summarize(path, label=None):
    rows = list(csv.DictReader(Path(path).open(newline="", encoding="utf-8")))
    if label:
        rows = [row for row in rows if row.get("label") == label]
    durations = [int(row["elapsed"]) for row in rows if row.get("elapsed", "").isdigit()]
    success = sum(row.get("success", "false").lower() == "true" for row in rows)
    start = [int(row["timeStamp"]) for row in rows if row.get("timeStamp", "").isdigit()]
    end = [int(row["timeStamp"]) + int(row.get("elapsed", 0)) for row in rows if row.get("timeStamp", "").isdigit()]
    window = max(end) - min(start) if start and end else 0
    return {
        "file": str(path),
        "total_requests": len(rows),
        "successful_requests": success,
        "failed_requests": len(rows) - success,
        "error_rate": round((len(rows) - success) / len(rows), 6) if rows else None,
        "average_ms": round(statistics.mean(durations), 3) if durations else None,
        "p50_ms": percentile(durations, 0.50),
        "p95_ms": percentile(durations, 0.95),
        "p99_ms": percentile(durations, 0.99),
        "throughput_requests_per_second": round(len(rows) / (window / 1000), 3) if window else None,
        "note": "HTTP-level JMeter metrics only; model/database/Kafka timings require application trace telemetry.",
    }


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        raise SystemExit("usage: python analyze_jtl.py input.jtl [--label LABEL] [--output summary.json]")
    input_path = sys.argv[1]
    label = None
    output = None
    index = 2
    while index < len(sys.argv):
        if sys.argv[index] == "--label":
            label = sys.argv[index + 1]
            index += 2
        elif sys.argv[index] == "--output":
            output = sys.argv[index + 1]
            index += 2
        else:
            raise SystemExit(f"unknown argument: {sys.argv[index]}")
    result = summarize(input_path, label=label)
    if output:
        Path(output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))
