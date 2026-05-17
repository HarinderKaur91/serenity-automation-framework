#!/usr/bin/env python3
"""Parse Maven Failsafe XML reports.

Usage:
    python3 parse_failsafe.py count     # prints total failed+error count
    python3 parse_failsafe.py classes   # prints comma-separated FQCNs of affected test classes
"""
import os
import sys
import xml.etree.ElementTree as ET

mode = sys.argv[1] if len(sys.argv) > 1 else 'count'
count = 0
classes = set()
base = 'target/failsafe-reports'

if os.path.isdir(base):
    for root, _dirs, files in os.walk(base):
        for f in files:
            if f.endswith('.xml') and f.startswith('TEST-'):
                try:
                    tree = ET.parse(os.path.join(root, f))
                    r = tree.getroot()
                    count += (
                        int(r.get('failures', '0'))
                        + int(r.get('errors', '0'))
                    )
                    for tc in r.findall('testcase'):
                        if (
                            tc.find('failure') is not None
                            or tc.find('error') is not None
                        ):
                            cn = tc.get('classname', '')
                            if cn:
                                classes.add(cn)
                except Exception:
                    pass

if mode == 'count':
    print(count)
else:
    print(','.join(sorted(classes)))
