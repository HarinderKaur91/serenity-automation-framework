#!/usr/bin/env python3
"""Build a small standalone HTML email summary from Maven Failsafe XML reports.

The output is a single self-contained HTML file (no external assets) that:
  - Renders a pass/fail/skipped doughnut chart using inlined Chart.js (UMD build).
  - Renders a per-class horizontal bar chart of pass/fail/skipped counts.
  - Lists failed scenarios with their failure messages.
  - Stays well under 1 MB so it can be attached to email without Gmail blocks.

Usage:
    python3 build_email_summary.py <failsafe_dir> <output_html> [run_url] [env_name]
"""
from __future__ import annotations

import html
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

CHARTJS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"
CHARTJS_CACHE = Path(__file__).parent / ".cache" / "chart.umd.js"


def fetch_chartjs() -> str:
    """Fetch Chart.js UMD bundle (cached locally between runs)."""
    if CHARTJS_CACHE.exists() and CHARTJS_CACHE.stat().st_size > 50_000:
        return CHARTJS_CACHE.read_text(encoding="utf-8")
    CHARTJS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(CHARTJS_URL, timeout=30) as resp:
            data = resp.read().decode("utf-8")
        CHARTJS_CACHE.write_text(data, encoding="utf-8")
        return data
    except Exception as exc:  # pragma: no cover - network optional
        print(f"⚠️  Could not fetch Chart.js ({exc}); summary will render without charts.", file=sys.stderr)
        return ""


def parse_failsafe(base: Path) -> dict:
    """Scan failsafe XMLs and return per-class + overall counts and failures."""
    classes: dict[str, dict] = {}
    failures: list[dict] = []
    totals = {"passed": 0, "failed": 0, "skipped": 0}

    if not base.is_dir():
        return {"classes": classes, "failures": failures, "totals": totals}

    for path in sorted(base.rglob("TEST-*.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue

        classname_attr = root.get("name") or path.stem
        class_short = classname_attr.rsplit(".", 1)[-1]
        bucket = classes.setdefault(
            class_short,
            {"passed": 0, "failed": 0, "skipped": 0, "fqcn": classname_attr},
        )

        for tc in root.findall("testcase"):
            name = tc.get("name", "<unnamed>")
            tc_class = tc.get("classname", classname_attr)
            failure_el = tc.find("failure") or tc.find("error")
            skipped_el = tc.find("skipped")

            if failure_el is not None:
                bucket["failed"] += 1
                totals["failed"] += 1
                msg = (failure_el.get("message") or failure_el.text or "").strip()
                # Keep the message reasonably short for the email
                if len(msg) > 600:
                    msg = msg[:600] + "..."
                failures.append(
                    {
                        "class": tc_class.rsplit(".", 1)[-1],
                        "name": name,
                        "message": msg,
                    }
                )
            elif skipped_el is not None:
                try:
                    has_evidence = float(tc.get("time", "0") or "0") > 0
                except ValueError:
                    has_evidence = False
                if has_evidence:
                    bucket["skipped"] += 1
                    totals["skipped"] += 1
            else:
                bucket["passed"] += 1
                totals["passed"] += 1

    return {"classes": classes, "failures": failures, "totals": totals}


def render_html(report: dict, chartjs_src: str, run_url: str, env_name: str) -> str:
    totals = report["totals"]
    classes = report["classes"]
    failures = report["failures"]

    total_tests = totals["passed"] + totals["failed"] + totals["skipped"]
    overall_status = (
        "ALL PASSED" if totals["failed"] == 0 and totals["skipped"] == 0
        else ("FAILURES DETECTED" if totals["failed"] > 0 else "SKIPPED PRESENT")
    )
    status_color = (
        "#16a34a" if overall_status == "ALL PASSED"
        else ("#dc2626" if overall_status == "FAILURES DETECTED" else "#d97706")
    )

    class_labels = list(classes.keys())
    class_passed = [classes[c]["passed"] for c in class_labels]
    class_failed = [classes[c]["failed"] for c in class_labels]
    class_skipped = [classes[c]["skipped"] for c in class_labels]

    failure_rows = "".join(
        f"<tr><td>{html.escape(f['class'])}</td>"
        f"<td>{html.escape(f['name'])}</td>"
        f"<td><pre>{html.escape(f['message'])}</pre></td></tr>"
        for f in failures
    ) or '<tr><td colspan="3" style="text-align:center;color:#6b7280;padding:18px;">No failures 🎉</td></tr>'

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    chartjs_block = f"<script>{chartjs_src}</script>" if chartjs_src else ""
    charts_init = """
        const fmt = (n) => String(n);
        const doughnutCtx = document.getElementById('doughnut');
        if (doughnutCtx && window.Chart) {
          new Chart(doughnutCtx, {
            type: 'doughnut',
            data: {
              labels: ['Passed', 'Failed', 'Skipped'],
              datasets: [{
                data: [DATA_PASSED, DATA_FAILED, DATA_SKIPPED],
                backgroundColor: ['#16a34a', '#dc2626', '#d97706'],
                borderWidth: 0
              }]
            },
            options: {
              responsive: true,
              plugins: {
                legend: { position: 'bottom' },
                tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${fmt(ctx.parsed)}` } }
              },
              cutout: '60%'
            }
          });
        }
        const barCtx = document.getElementById('byClass');
        if (barCtx && window.Chart) {
          new Chart(barCtx, {
            type: 'bar',
            data: {
              labels: DATA_CLASS_LABELS,
              datasets: [
                { label: 'Passed',  data: DATA_CLASS_PASSED,  backgroundColor: '#16a34a' },
                { label: 'Failed',  data: DATA_CLASS_FAILED,  backgroundColor: '#dc2626' },
                { label: 'Skipped', data: DATA_CLASS_SKIPPED, backgroundColor: '#d97706' }
              ]
            },
            options: {
              indexAxis: 'y',
              responsive: true,
              scales: {
                x: { stacked: true, beginAtZero: true, ticks: { precision: 0 } },
                y: { stacked: true }
              },
              plugins: { legend: { position: 'bottom' } }
            }
          });
        }
    """
    charts_init = (
        charts_init
        .replace("DATA_PASSED", json.dumps(totals["passed"]))
        .replace("DATA_FAILED", json.dumps(totals["failed"]))
        .replace("DATA_SKIPPED", json.dumps(totals["skipped"]))
        .replace("DATA_CLASS_LABELS", json.dumps(class_labels))
        .replace("DATA_CLASS_PASSED", json.dumps(class_passed))
        .replace("DATA_CLASS_FAILED", json.dumps(class_failed))
        .replace("DATA_CLASS_SKIPPED", json.dumps(class_skipped))
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Test Report Summary [{html.escape(env_name)}]</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         margin: 0; padding: 24px; background: #f8fafc; color: #0f172a; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .sub {{ color: #475569; margin-bottom: 18px; font-size: 13px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px;
            color: white; font-weight: 600; font-size: 13px;
            background: {status_color}; margin-left: 8px; vertical-align: middle; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px;
           margin-bottom: 18px; }}
  .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 12px;
           padding: 16px; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }}
  .card h2 {{ font-size: 14px; margin: 0 0 8px; color: #334155;
              text-transform: uppercase; letter-spacing: 0.04em; }}
  .stat {{ display: flex; justify-content: space-around; text-align: center;
           padding: 12px 0; }}
  .stat div b {{ display: block; font-size: 26px; }}
  .stat div span {{ font-size: 12px; color: #64748b; }}
  .green {{ color: #16a34a; }} .red {{ color: #dc2626; }} .amber {{ color: #d97706; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #e2e8f0;
            vertical-align: top; }}
  th {{ background: #f1f5f9; font-weight: 600; color: #334155; }}
  pre {{ margin: 0; white-space: pre-wrap; word-break: break-word;
         font-family: SFMono-Regular, Consolas, monospace; font-size: 12px;
         color: #b91c1c; max-height: 160px; overflow: auto; }}
  a {{ color: #2563eb; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .footer {{ margin-top: 18px; color: #64748b; font-size: 12px; }}
  @media (max-width: 700px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
  <h1>Serenity Test Summary — {html.escape(env_name)}
    <span class="badge">{overall_status}</span></h1>
  <div class="sub">
    Generated {generated_at} · Total tests: <b>{total_tests}</b>
    {f' · <a href="{html.escape(run_url)}">Open GitHub Actions run</a>' if run_url else ''}
  </div>

  <div class="grid">
    <div class="card">
      <h2>Overall Outcome</h2>
      <div class="stat">
        <div><b class="green">{totals['passed']}</b><span>Passed</span></div>
        <div><b class="red">{totals['failed']}</b><span>Failed</span></div>
        <div><b class="amber">{totals['skipped']}</b><span>Skipped</span></div>
      </div>
      <canvas id="doughnut" height="180"></canvas>
    </div>
    <div class="card">
      <h2>By Test Class</h2>
      <canvas id="byClass" height="220"></canvas>
    </div>
  </div>

  <div class="card">
    <h2>Failed Scenarios</h2>
    <table>
      <thead><tr><th>Class</th><th>Scenario</th><th>Failure</th></tr></thead>
      <tbody>{failure_rows}</tbody>
    </table>
  </div>

  <p class="footer">
    The full Serenity report (with screenshots, step-by-step logs, and drilldown
    pages) is published as a workflow artifact on the GitHub Actions run linked
    above. — Self-Healing Test Framework
  </p>

  {chartjs_block}
  <script>{charts_init}</script>
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2

    failsafe_dir = Path(sys.argv[1])
    output_html = Path(sys.argv[2])
    run_url = sys.argv[3] if len(sys.argv) > 3 else ""
    env_name = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("ENV_NAME", "qa")

    report = parse_failsafe(failsafe_dir)
    chartjs_src = fetch_chartjs()
    output_html.write_text(
        render_html(report, chartjs_src, run_url, env_name),
        encoding="utf-8",
    )

    size_kb = output_html.stat().st_size / 1024
    print(
        f"✅ Wrote {output_html} "
        f"({size_kb:.1f} KB; passed={report['totals']['passed']}, "
        f"failed={report['totals']['failed']}, skipped={report['totals']['skipped']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
