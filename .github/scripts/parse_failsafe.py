#!/usr/bin/env python3
"""Parse Maven Failsafe XML reports.

Usage:
    python3 parse_failsafe.py count           # prints total failed+error testcase count
    python3 parse_failsafe.py retriable-count # prints total failed+error+skipped testcase count
    python3 parse_failsafe.py skipped-count   # prints total skipped testcase count
    python3 parse_failsafe.py classes         # prints comma-separated FQCNs of affected test classes
"""
import os
import sys
import xml.etree.ElementTree as ET

mode = sys.argv[1] if len(sys.argv) > 1 else 'count'
count = 0
skipped_count = 0
classes = set()
base = 'target/failsafe-reports'

if os.path.isdir(base):
    for root, _dirs, files in os.walk(base):
        for f in files:
            if f.endswith('.xml') and f.startswith('TEST-'):
                try:
                    tree = ET.parse(os.path.join(root, f))
                    r = tree.getroot()
                    for tc in r.findall('testcase'):
                        has_failure = tc.find('failure') is not None
                        has_error = tc.find('error') is not None
                        has_skipped = tc.find('skipped') is not None

                        if has_failure or has_error:
                            count += 1
                            cn = tc.get('classname', '')
                            if cn:
                                classes.add(cn)
                        if has_skipped:
                            skipped_count += 1
                except Exception:
                    pass

if mode == 'count':
    print(count)
elif mode == 'retriable-count':
    print(count + skipped_count)
elif mode == 'skipped-count':
    print(skipped_count)
else:
    print(','.join(sorted(classes)))
