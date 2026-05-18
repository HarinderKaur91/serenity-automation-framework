#!/usr/bin/env python3
"""Build a standalone HTML diff report comparing two Maven Failsafe report sets.

Used by the post-PR-merge rerun to show what changed between the initial
(failing) run and the post-merge full-suite re-run.

Usage:
    python3 build_comparison_report.py <initial_failsafe_dir> <current_failsafe_dir> <output_html> [run_url] [env_name]
"""
from __future__ import annotations

import html
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


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


def render(initial: dict, current: dict, run_url: str, env_name: str) -> str:
    init_keys = set(initial["failures"].keys())
    curr_keys = set(current["failures"].keys())

    fixed = sorted(init_keys - curr_keys)
    still_failing = sorted(init_keys & curr_keys)
    newly_failing = sorted(curr_keys - init_keys)

    def fmt_failure(src: dict, key: str) -> str:
        f = src["failures"][key]
        return (
            f"<tr><td><code>{html.escape(f['class'])}</code></td>"
            f"<td>{html.escape(f['scenario'])}</td>"
            f"<td><pre>{html.escape(f['message'])}</pre></td></tr>"
        )

    def section(title: str, items: list[str], src: dict, kind: str) -> str:
        if not items:
            return (
                f"<h2>{title} <span class='count'>(0)</span></h2>"
                f"<p class='muted'>None.</p>"
            )
        rows = "\n".join(fmt_failure(src, k) for k in items)
        return (
            f"<h2 class='{kind}'>{title} <span class='count'>({len(items)})</span></h2>"
            f"<table><thead><tr><th>Class</th><th>Scenario</th><th>Message</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    init_tot = initial["totals"]
    curr_tot = current["totals"]
    delta_failed = curr_tot["failed"] - init_tot["failed"]
    delta_passed = curr_tot["passed"] - init_tot["passed"]
    delta_skipped = curr_tot["skipped"] - init_tot["skipped"]

    def delta_str(n: int) -> str:
        if n > 0:
            return f"<span class='delta-bad'>+{n}</span>"
        if n < 0:
            return f"<span class='delta-good'>{n}</span>"
        return "<span class='muted'>0</span>"

    overall_verdict = (
        ("✅ All previously failing scenarios now pass.", "good")
        if not still_failing and not newly_failing
        else ("⚠️ Failures still present after Copilot fix.", "warn")
        if still_failing or newly_failing
        else ("ℹ️ No differences.", "muted")
    )
    verdict_text, verdict_cls = overall_verdict

    run_link = (
        f"<p><a href='{html.escape(run_url)}' target='_blank'>View workflow run →</a></p>"
        if run_url
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<title>Comparison: Initial vs Post-Merge — {html.escape(env_name)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; padding: 24px; color: #1f2328; background: #f6f8fa; }}
  h1 {{ margin: 0 0 4px; font-size: 22px; }}
  h2 {{ margin-top: 28px; font-size: 18px; border-bottom: 1px solid #d0d7de; padding-bottom: 6px; }}
  h2.good {{ color: #1a7f37; }}
  h2.warn {{ color: #9a3412; }}
  h2.new  {{ color: #b91c1c; }}
  .count {{ font-weight: normal; color: #57606a; font-size: 14px; }}
  .muted {{ color: #57606a; }}
  .delta-good {{ color: #1a7f37; font-weight: 600; }}
  .delta-bad {{ color: #b91c1c; font-weight: 600; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 8px; background: white; }}
  th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; vertical-align: top; text-align: left; font-size: 13px; }}
  th {{ background: #f6f8fa; }}
  pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; font-size: 12px; color: #59351f; }}
  .summary {{ display: flex; gap: 16px; margin-top: 12px; flex-wrap: wrap; }}
  .card {{ background: white; padding: 12px 16px; border: 1px solid #d0d7de; border-radius: 6px; min-width: 160px; }}
  .card .label {{ color: #57606a; font-size: 12px; text-transform: uppercase; }}
  .card .value {{ font-size: 22px; font-weight: 600; margin-top: 4px; }}
  .verdict {{ padding: 12px 16px; border-radius: 6px; margin-top: 12px; font-weight: 600; }}
  .verdict.good {{ background: #dcfce7; color: #166534; }}
  .verdict.warn {{ background: #fef3c7; color: #92400e; }}
  .verdict.muted {{ background: #f3f4f6; color: #374151; }}
</style>
</head>
<body>
  <h1>📊 Initial Run vs Post-PR-Merge Run</h1>
  <p class='muted'>Environment: <strong>{html.escape(env_name)}</strong> · Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z</p>
  {run_link}

  <div class='verdict {verdict_cls}'>{verdict_text}</div>

  <div class='summary'>
    <div class='card'><div class='label'>Failed</div><div class='value'>{init_tot['failed']} → {curr_tot['failed']} {delta_str(delta_failed)}</div></div>
    <div class='card'><div class='label'>Passed</div><div class='value'>{init_tot['passed']} → {curr_tot['passed']} {delta_str(delta_passed)}</div></div>
    <div class='card'><div class='label'>Skipped</div><div class='value'>{init_tot['skipped']} → {curr_tot['skipped']} {delta_str(delta_skipped)}</div></div>
  </div>

  {section('✅ Fixed (failed before, pass now)', fixed, initial, 'good')}
  {section('❌ Still Failing', still_failing, current, 'warn')}
  {section('🆕 Newly Failing (regressions introduced by the fix)', newly_failing, current, 'new')}
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

    html_str = render(initial, current, run_url, env_name)
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
