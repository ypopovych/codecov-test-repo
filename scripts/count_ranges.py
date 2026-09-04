"""Count distinct uncovered ranges in coverage.xml, using Codecov's grouping rule.

Codecov's worker (services/notification/notifiers/checks/base.py,
get_lines_to_annotate) starts a new annotation range whenever the next
uncovered line is not previous + 1. This reproduces that so we can assert the
fixture really produces N separate ranges rather than a few merged ones.
"""

import sys
import xml.etree.ElementTree as ET

root = ET.parse("coverage.xml").getroot()
missing = sorted(
    int(line.get("number"))
    for cls in root.iter("class")
    for line in cls.iter("line")
    if line.get("hits") == "0"
)

ranges = []
for n in missing:
    if ranges and n == ranges[-1][1] + 1:
        ranges[-1][1] = n
    else:
        ranges.append([n, n])

print(f"uncovered lines : {len(missing)}")
print(f"distinct ranges : {len(ranges)}")
print(f"ranges          : {', '.join(str(a) if a == b else f'{a}-{b}' for a, b in ranges)}")

# Only meaningful once the fixture is present; the baseline branch has none.
if len(missing) >= 55 and len(ranges) < 55:
    sys.exit(f"ERROR: expected ~60 distinct ranges, got {len(ranges)} (they merged)")
