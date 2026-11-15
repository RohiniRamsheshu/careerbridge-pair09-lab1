"""Generate simple SVG evidence graphs from actual summary JSON files."""
import json
import csv
from pathlib import Path


def graph(rows, title, x_label, y_label, output):
    width, height, left, bottom = 900, 520, 90, 390
    max_y = max(row[1] for row in rows) or 1
    max_x = max(row[0] for row in rows) or 1
    points = []
    for x, y in rows:
        px = left + (x / max_x) * 740
        py = bottom - (y / max_y) * 300
        points.append(f"{px:.1f},{py:.1f}")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           f'<text x="450" y="35" text-anchor="middle" font-family="Arial" font-size="20">{title}</text>',
           f'<line x1="{left}" y1="{bottom}" x2="830" y2="{bottom}" stroke="black"/>',
           f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="90" stroke="black"/>',
           f'<polyline points="{" ".join(points)}" fill="none" stroke="#0b4f47" stroke-width="3"/>']
    for (x, y), point in zip(rows, points):
        px, py = point.split(",")
        svg.append(f'<circle cx="{px}" cy="{py}" r="5" fill="#b28b35"/><text x="{px}" y="{float(py)-10:.1f}" text-anchor="middle" font-family="Arial" font-size="12">{y:.0f}</text><text x="{px}" y="{bottom+22}" text-anchor="middle" font-family="Arial" font-size="12">{x}</text>')
    svg += [f'<text x="450" y="475" text-anchor="middle" font-family="Arial">{x_label}</text>', f'<text x="18" y="240" transform="rotate(-90 18 240)" text-anchor="middle" font-family="Arial">{y_label}</text>', '</svg>']
    Path(output).write_text("\n".join(svg) + "\n", encoding="utf-8")


if __name__ == "__main__":
    result_dir = Path("performance/results")
    crud = []
    assistant = []
    for users in (100, 200, 300, 400, 500):
        crud.append((users, json.loads((result_dir / f"crud-{users}-summary.json").read_text())["average_ms"]))
    for users in (5, 10, 20, 50):
        assistant.append((users, json.loads((result_dir / f"assistant-{users}-summary.json").read_text())["average_ms"]))
    graph(crud, "CareerBridge CRUD average latency", "Concurrent users", "Average response time (ms)", result_dir / "crud-average-vs-concurrency.svg")
    graph(assistant, "CareerBridge assistant chat average latency", "Concurrent users", "Average response time (ms)", result_dir / "assistant-average-vs-concurrency.svg")
    with (result_dir / "crud-summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["concurrency", "requests", "average_ms", "p50_ms", "p95_ms", "p99_ms", "throughput", "error_rate"])
        for users, _ in crud:
            row = json.loads((result_dir / f"crud-{users}-summary.json").read_text())
            writer.writerow([users, row["total_requests"], row["average_ms"], row["p50_ms"], row["p95_ms"], row["p99_ms"], row["throughput_requests_per_second"], row["error_rate"]])
    with (result_dir / "assistant-summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["concurrency", "requests", "average_ms", "p50_ms", "p95_ms", "p99_ms", "throughput", "error_rate"])
        for users, _ in assistant:
            row = json.loads((result_dir / f"assistant-{users}-summary.json").read_text())
            writer.writerow([users, row["total_requests"], row["average_ms"], row["p50_ms"], row["p95_ms"], row["p99_ms"], row["throughput_requests_per_second"], row["error_rate"]])
    print("graphs=2")
