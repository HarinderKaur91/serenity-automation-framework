#!/usr/bin/env python3
"""Parse Maven Failsafe XML reports.

Usage:
    python3 parse_failsafe.py count     # prints total failed+error count
    python3 parse_failsafe.py classes   # prints comma-separated FQCNs of failed/error test classes
"""
import os
import sys
import xml.etree.ElementTree as ET

def collect_results(base='target/failsafe-reports'):
    count = 0
    classes = set()

    if os.path.isdir(base):
        for root, _dirs, files in os.walk(base):
            for filename in files:
                if filename.endswith('.xml') and filename.startswith('TEST-'):
                    try:
                        tree = ET.parse(os.path.join(root, filename))
                        report = tree.getroot()
                        count += (
                            int(report.get('failures', '0'))
                            + int(report.get('errors', '0'))
                        )
                        for testcase in report.findall('testcase'):
                            if (
                                testcase.find('failure') is not None
                                or testcase.find('error') is not None
                            ):
                                classname = testcase.get('classname', '')
                                if classname:
                                    classes.add(classname)
                    except Exception:
                        pass

    return count, classes


def main(argv=None):
    mode = (argv or sys.argv[1:])[0] if (argv or sys.argv[1:]) else 'count'
    count, classes = collect_results()

    if mode == 'count':
        print(count)
    else:
        print(','.join(sorted(classes)))


if __name__ == '__main__':
    main()
