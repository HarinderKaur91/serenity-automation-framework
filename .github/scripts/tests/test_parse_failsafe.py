import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / 'parse_failsafe.py'
SPEC = importlib.util.spec_from_file_location('parse_failsafe', SCRIPT_PATH)
parse_failsafe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parse_failsafe)


class ParseFailsafeTest(unittest.TestCase):
    def test_collect_results_ignores_skipped_testcases(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            reports_dir = Path(tmp_dir) / 'target' / 'failsafe-reports'
            reports_dir.mkdir(parents=True)
            (reports_dir / 'TEST-skipped.xml').write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<testsuite tests="3" failures="0" errors="0" skipped="2">
    <testcase classname="example.PassingTest" name="passes" />
    <testcase classname="example.SkippedTest" name="isSkipped">
        <skipped />
    </testcase>
    <testcase classname="example.AnotherSkippedTest" name="isAlsoSkipped">
        <skipped />
    </testcase>
</testsuite>
""",
                encoding='utf-8',
            )

            count, classes = parse_failsafe.collect_results(str(reports_dir))

            self.assertEqual(0, count)
            self.assertEqual(set(), classes)

    def test_collect_results_counts_failures_and_errors_only(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            reports_dir = Path(tmp_dir) / 'target' / 'failsafe-reports'
            reports_dir.mkdir(parents=True)
            (reports_dir / 'TEST-failed.xml').write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<testsuite tests="3" failures="1" errors="1" skipped="1">
    <testcase classname="example.PassingTest" name="passes" />
    <testcase classname="example.FailingTest" name="fails">
        <failure message="boom" />
    </testcase>
    <testcase classname="example.ErrorTest" name="errors">
        <error message="kaboom" />
    </testcase>
    <testcase classname="example.SkippedTest" name="skipped">
        <skipped />
    </testcase>
</testsuite>
""",
                encoding='utf-8',
            )

            count, classes = parse_failsafe.collect_results(str(reports_dir))

            self.assertEqual(2, count)
            self.assertEqual(
                {'example.FailingTest', 'example.ErrorTest'},
                classes,
            )


if __name__ == '__main__':
    unittest.main()
