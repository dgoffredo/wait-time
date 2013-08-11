from sys import argv, stdout
import re

source = open(argv[1])
inExtStr = False
for line in source:
    if re.search(r"'''", line):
        inExtStr = not inExtStr # toggle
        continue
    elif not inExtStr and not re.match(r'^[ \t]*#', line):
        stdout.write(line)
