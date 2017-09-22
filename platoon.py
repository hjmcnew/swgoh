#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sqlite3
import sys
from collections import defaultdict

phase = int(sys.argv[1])
stars = phase + 1

output = {}
report = defaultdict(lambda: defaultdict(dict))

conn = sqlite3.connect('sqlite-db-location')
c = conn.cursor()

values = ('light',)
c.execute('SELECT DISTINCT character FROM toons WHERE side=? ORDER BY character', values)

toons = c.fetchall()

for toon in toons:
    values = (''.join(toon), stars)
    c.execute('SELECT count(*) AS count FROM toons WHERE character = ? AND star >= ? GROUP BY character', values)
    row = c.fetchone()
    if row:
        tooncount = row[0]
    else:
        tooncount = 0

    output[values[0]] = tooncount

sortedoutput = sorted(output.items(), key=lambda x: x[1], reverse=True)

print("<table border='0'>")
print(" <tr>")
print("  <th colspan='3'>")
print("   Available character counts for Phase %s" % (phase,))
print("  </th>")
print(" </tr>")
for line in sortedoutput:
    print(" <tr>")
    if line[1] == 0:
        print("  <td>%s</td><td align='right'>%s</td><td><b>Platoons containing this character cannot be completed.</b></td>"
              % (line[0].encode('utf-8'), line[1]))
    elif line[1] > 12:
        c.execute('''SELECT user, level, gear, star
                     FROM toons
                     WHERE character = ?
                     AND star >= ?
                     AND gear < 8
                     AND level < 85
                     ORDER BY gear, level, star
                     LIMIT 12''', (line[0], stars))
        rows = c.fetchall()
        for row in rows:
            report[row[0]][line[0]] = "%s*/G%s/L%s" % (row[3], row[2], row[1])
        print("  <td>%s</td><td align='right'>%s</td><td>&nbsp;</td>" % (line[0].encode('utf-8'), line[1]))
    elif line[1] > 0:
        c.execute('''SELECT user, level, gear, star
                     FROM toons
                     WHERE character = ?
                     AND star >= ?
                     ORDER BY gear, level, star''', (line[0], stars))
        rows = c.fetchall()
        for row in rows:
            report[row[0]][line[0]] = "%s*/G%s/L%s" % (row[3], row[2], row[1])
        print("  <td>%s</td><td align='right'>%s</td><td>&nbsp;</td>" % (line[0].encode('utf-8'), line[1]))
    print(" </tr>")
print("</table>")

print("<h2>Suggested Platoons for Phase %s</h2>" % (phase,))

print("<pre>")
for user in sorted(report.iterkeys()):
    print(user)
    for character in sorted(report[user].iterkeys()):
        print("    %s - %s" % (character.encode('utf-8'), report[user][character]))
    print("")
print("</pre>")
print("</body>")
print("</html>")

conn.close()
