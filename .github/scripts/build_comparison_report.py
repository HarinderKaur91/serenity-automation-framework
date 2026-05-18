#!/usr/bin/env python3
"""Build a standalone HTML diff report comparing two Maven Failsafe report sets.

Used by the post-PR-merge rerun to show what changed between the initial
(failing) run and the post-merge full-suite re-run.

Usage:
    python3 build_comparison_report.py <initial_failsafe_dir> <current_failsafe_dir> <output_html> [run_url] [env_name]
"""
from __future__ import annotations

import html
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

CHARTJS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"
CHARTJS_CACHE = Path(__file__).parent / ".cache" / "chart.umd.js"


def fetch_chartjs() -> str:
    if CHARTJS_CACHE.exists() and CHARTJS_CACHE.stat().st_size > 50_000:
        return CHARTJS_CACHE.read_text(encoding="utf-8")
    CHARTJS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(CHARTJS_URL, timeout=30) as resp:
            data = resp.read().decode("utf-8")
        CHARTJS_CACHE.write_text(data, encoding="utf-8")
        return data
    except Exception as exc:
        print(f"⚠️  Could not fetch Chart.js ({exc}); charts will be omitted.", file=sys.stderr)
        return ""


def parse(base: Path) -> dict:
    classes: dict[str, dict] = {}
    failures: dict[str, dict] = {}  # key = "class::scenario" → {class, scenario, message}
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
        bucket = classes.setdefault(class_short, {"passed": 0, "failed": 0, "skipped": 0})
        for tc in root.findall("testcase"):
            name = tc.get("name", "<unnamed>")
            tc_class = (tc.get("classname", classname_attr) or "").rsplit(".", 1)[-1]
            failure_el = tc.find("failure")
            if failure_el is None:
                failure_el = tc.find("error")
            skipped_el = tc.find("skipped")
            if failure_el is not None:
                bucket["failed"] += 1
                totals["failed"] += 1
                msg = (failure_el.get("message") or failure_el.text or "").strip()
                if len(msg) > 400:
                    msg = msg[:400] + "..."
                key = f"{tc_class}::{name}"
                failures[key] = {"class": tc_class, "scenario": name, "message": msg}
            elif skipped_el is not None:
                bucket["skipped"] += 1
                totals["skipped"] += 1
            else:
                bucket["passed"] += 1
                totals["passed"] += 1
    return {"classes": classes, "failures": failures, "totals": totals}


def render(initial: dict, current: dict, run_url: str, env_name: str, chartjs_src: str) -> str:
    init_keys = set(initial["failures"].keys())
    curr_keys = set(current["failures"].keys())

    fixed = sorted(init_keys - curr_keys)
    still_failing = sorted(init_keys & curr_keys)
    newly_failing = sorted(curr_keys - init_keys)

    init_tot = initial["totals"]
    curr_tot = current["totals"]
    delta_failed = curr_tot["failed"] - init_tot["failed"]
    delta_passed = curr_tot["passed"] - init_tot["passed"]
    delta_skipped = curr_tot["skipped"] - init_tot["skipped"]

    # ── Verdict ──────────────────────────────────────────────────────────────
    if not still_failing and not newly_failing:
        verdict_text = "✅ All previously failing scenarios now pass — Copilot fix successful!"
        verdict_cls = "good"
        badge_text = "FIXED"
        badge_color = "#16a34a"
    elif newly_failing:
        verdict_text = "🚨 Regressions introduced by the Copilot fix — manual review required."
        verdict_cls = "danger"
        badge_text = "REGRESSIONS"
        badge_color = "#b91c1c"
    else:
        verdict_text = "⚠️ Failures still present after Copilot fix — manual investigation required."
        verdict_cls = "warn"
        badge_text = "STILL FAILING"
        badge_color = "#d97706"

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    run_link_html = (
        f' · <a href="{html.escape(run_url)}">Open GitHub Actions run</a>'
        if run_url else ""
    )

    def delta_badge(n: int) -> str:
        if n > 0:
            return f"<span class='delta-bad'>▲ +{n}</span>"
        if n < 0:
            return f"<span class='delta-good'>▼ {n}</span>"
        return "<span class='delta-neutral'>= 0</span>"

    def failure_rows_html(items: list, src: dict) -> str:
        rows = []
        for key in items:
            f = src["failures"][key]
            rows.append(
                f"<tr>"
                f"<td><code>{html.escape(f['class'])}</code></td>"
                f"<td>{html.escape(f['scenario'])}</td>"
                f"<td><pre>{html.escape(f['message'])}</pre></td>"
                f"</tr>"
            )
        return "\n".join(rows) if rows else '<tr><td colspan="3" class="empty">None 🎉</td></tr>'

    def section_card(title: str, count: int, items: list, src: dict, header_cls: str) -> str:
        return f"""
        <div class="card full">
          <h2 class="section-title {header_cls}">{title} <span class="count-badge">{count}</span></h2>
          <table>
            <thead><tr><th>Class</th><th>Scenario</th><th>Failure Message</th></tr></thead>
            <tbody>{failure_rows_html(items, src)}</tbody>
          </table>
        </div>"""

    chartjs_block = f"<script>{chartjs_src}</script>" if chartjs_src else ""

    bar_chart_js = """
    const barCtx = document.getElementById('deltaBar');
    if (barCtx && window.Chart) {
      new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: ['Failed', 'Passed', 'Skipped'],
          datasets: [
            { label: 'Initial Run',    data: INIT_COUNTS, backgroundColor: '#94a3b8' },
            { label: 'Post-Merge Run', data: CURR_COUNTS, backgroundColor: '#2563eb' }
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'bottom' } },
          scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
        }
      });
    }
    const dInit = document.getElementById('doughnutInit');
    if (dInit && window.Chart) {
      new Chart(dInit, {
        type: 'doughnut',
        data: {
          labels: ['Passed','Failed','Skipped'],
          datasets: [{ data: INIT_DOUGHNUT, backgroundColor: ['#16a34a','#dc2626','#d97706'], borderWidth: 0 }]
        },
        options: { responsive: true, cutout: '60%', plugins: { legend: { position: 'bottom' } } }
      });
    }
    const dCurr = document.getElementById('doughnutCurr');
    if (dCurr && window.Chart) {
      new Chart(dCurr, {
        type: 'doughnut',
        data: {
          labels: ['Passed','Failed','Skipped'],
          datasets: [{ data: CURR_DOUGHNUT, backgroundColor: ['#16a34a','#dc2626','#d97706'], borderWidth: 0 }]
        },
        options: { responsive: true, cutout: '60%', plugins: { legend: { position: 'bottom' } } }
      });
    }
    """
    bar_chart_js = (
        bar_chart_js
        .replace("INIT_COUNTS", json.dumps([init_tot["failed"], init_tot["passed"], init_tot["skipped"]]))
        .replace("CURR_COUNTS", json.dumps([curr_tot["failed"], curr_tot["passed"], curr_tot["skipped"]]))
        .replace("INIT_DOUGHNUT", json.dumps([init_tot["passed"], init_tot["failed"], init_tot["skipped"]]))
        .replace("CURR_DOUGHNUT", json.dumps([curr_tot["passed"], curr_tot["failed"], curr_tot["skipped"]]))
    )

    init_total = sum(init_tot.values())
    curr_total = sum(curr_tot.values())

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Comparison Report [{html.escape(env_name)}]</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         margin: 0; padding: 24px; background: #f8fafc; color: #0f172a; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .sub {{ color: #475569; margin-bottom: 18px; font-size: 13px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px;
            color: white; font-weight: 600; font-size: 13px;
            background: {badge_color}; margin-left: 8px; vertical-align: middle; }}
  .verdict {{ padding: 14px 18px; border-radius: 10px; font-weight: 600;
              font-size: 15px; margin-bottom: 20px; }}
  .verdict.good   {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
  .verdict.warn   {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
  .verdict.danger {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }}
  .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 12px;
           padding: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.06); }}
  .card.full {{ grid-column: 1 / -1; margin-bottom: 16px; }}
  .card h2 {{ font-size: 13px; margin: 0 0 10px; color: #334155;
              text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }}
  .stat-value {{ font-size: 28px; font-weight: 700; margin: 6px 0 2px; }}
  .stat-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }}
  .stat-delta {{ font-size: 13px; margin-top: 4px; }}
  .green {{ color: #16a34a; }} .red {{ color: #dc2626; }} .amber {{ color: #d97706; }}
  .delta-good    {{ color: #16a34a; font-weight: 700; }}
  .delta-bad     {{ color: #dc2626; font-weight: 700; }}
  .delta-neutral {{ color: #64748b; }}
  .section-title {{ font-size: 15px; font-weight: 700; margin: 0 0 12px;
                    padding-bottom: 8px; border-bottom: 2px solid #e2e8f0;
                    text-transform: none; letter-spacing: 0; }}
  .section-title.good-hdr   {{ color: #15803d; border-color: #86efac; }}
  .section-title.warn-hdr   {{ color: #b45309; border-color: #fcd34d; }}
  .section-title.danger-hdr {{ color: #b91c1c; border-color: #fca5a5; }}
  .count-badge {{ display: inline-block; background: #e2e8f0; color: #334155;
                  border-radius: 999px; padding: 1px 10px; font-size: 12px;
                  font-weight: 600; margin-left: 8px; vertical-align: middle; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
  th {{ background: #f1f5f9; font-weight: 600; color: #334155; white-space: nowrap; }}
  pre {{ margin: 0; white-space: pre-wrap; word-break: break-word;
         font-family: SFMono-Regular, Consolas, monospace; font-size: 12px;
         color: #b91c1c; max-height: 140px; overflow: auto; }}
  code {{ font-family: SFMono-Regular, Consolas, monospace; font-size: 12px; color: #2563eb; }}
  td.empty {{ text-align: center; color: #6b7280; padding: 18px; }}
  a {{ color: #2563eb; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .chart-label {{ text-align: center; font-size: 12px; color: #475569; margin-top: 6px;
                  font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }}
  .footer {{ margin-top: 24px; color: #94a3b8; font-size: 12px; text-align: center; }}
  @media (max-width: 700px) {{ .grid-3, .grid-2 {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

  <h1>📊 Initial Run vs Post-PR-Merge Comparison
    <span class="badge">{badge_text}</span>
  </h1>
  <div class="sub">
    Environment: <strong>{html.escape(env_name)}</strong>
    &nbsp;·&nbsp; Generated {generated_at}{run_link_html}
  </div>

  <div class="verdict {verdict_cls}">{verdict_text}</div>

  <!-- Delta stat cards -->
  <div class="grid-3">
    <div class="card">
      <div class="stat-label">Failed</div>
      <div class="stat-value red">{init_tot['failed']} → {curr_tot['failed']}</div>
      <div class="stat-delta">{delta_badge(delta_failed)}</div>
    </div>
    <div class="card">
      <div class="stat-label">Passed</div>
      <div class="stat-value green">{init_tot['passed']} → {curr_tot['passed']}</div>
      <div class="stat-delta">{delta_badge(delta_passed)}</div>
    </div>
    <div class="card">
      <div class="stat-label">Skipped</div>
      <div class="stat-value amber">{init_tot['skipped']} → {curr_tot['skipped']}</div>
      <div class="stat-delta">{delta_badge(delta_skipped)}</div>
    </div>
  </div>

  <!-- Change summary cards -->
  <div class="grid-3">
    <div class="card">
      <div class="stat-label green">✅ Fixed</div>
      <div class="stat-value green">{len(fixed)}</div>
      <div class="stat-delta" style="color:#64748b;font-size:12px;">Failed before, now pass</div>
    </div>
    <div class="card">
      <div class="stat-label red">❌ Still Failing</div>
      <div class="stat-value red">{len(still_failing)}</div>
      <div class="stat-delta" style="color:#64748b;font-size:12px;">Failed in both runs</div>
    </div>
    <div class="card">
      <div class="stat-label" style="color:#b91c1c;">🆕 New Regressions</div>
      <div class="stat-value" style="color:#b91c1c;">{len(newly_failing)}</div>
      <div class="stat-delta" style="color:#64748b;font-size:12px;">Introduced by the fix</div>
    </div>
  </div>

  <!-- Doughnut charts -->
  <div class="grid-2">
    <div class="card">
      <h2>Initial Run Outcome</h2>
      <canvas id="doughnutInit" height="200"></canvas>
      <div class="chart-label">Initial Run — {init_total} tests</div>
    </div>
    <div class="card">
      <h2>Post-Merge Run Outcome</h2>
      <canvas id="doughnutCurr" height="200"></canvas>
      <div class="chart-label">Post-Merge Run — {curr_total} tests</div>
    </div>
  </div>

  <!-- Grouped bar chart -->
  <div class="card" style="margin-bottom:20px;">
    <h2>Side-by-Side Comparison</h2>
    <canvas id="deltaBar" height="120"></canvas>
  </div>

  <!-- Scenario tables -->
  {section_card('✅ Fixed — Scenarios now passing', len(fixed), fixed, initial, 'good-hdr')}
  {section_card('❌ Still Failing after fix', len(still_failing), still_failing, current, 'warn-hdr')}
  {section_card('🆕 New Regressions introduced by fix', len(newly_failing), newly_failing, current, 'danger-hdr')}

  <p class="footer">Self-Healing Test Framework · Serenity BDD · Auto-generated comparison report</p>

  {chartjs_block}
  <script>{bar_chart_js}</script>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(
            "Usage: build_comparison_report.py <initial_failsafe_dir> "
            "<current_failsafe_dir> <output_html> [run_url] [env_name]",
            file=sys.stderr,
        )
        return 2
    initial_dir = Path(argv[1])
    current_dir = Path(argv[2])
    out_path = Path(argv[3])
    run_url = argv[4] if len(argv) > 4 else ""
    env_name = argv[5] if len(argv) > 5 else "qa"

    initial = parse(initial_dir)
    current = parse(current_dir)
    chartjs_src = fetch_chartjs()

    html_str = render(initial, current, run_url, env_name, chartjs_src)
    out_path.write_text(html_str, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024.0
    print(
        f"✅ Wrote {out_path} ({size_kb:.1f} KB; "
        f"initial: {sum(initial['totals'].values())} tests, "
        f"current: {sum(current['totals'].values())} tests, "
        f"fixed/still/new = "
        f"{len(set(initial['failures']) - set(current['failures']))}/"
        f"{len(set(initial['failures']) & set(current['failures']))}/"
        f"{len(set(current['failures']) - set(initial['failures']))})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
