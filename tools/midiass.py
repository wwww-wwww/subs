#!/usr/bin/env python3
import sys, re, subprocess

re_blank = r"^Dialogue.*,.*,.*,.*,.*,.*,.*,.*,.*,({[^}]*})*\\blank$"


def main():
  if len(sys.argv) < 2:
    print("Usage:", sys.argv[0], "MIDI", "TEXT")
    return

  midicsv = subprocess.Popen(["midicsv", sys.argv[1]],
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
  midicsv2ass = subprocess.run(["midicsv2ass", sys.argv[2]],
                               stdin=midicsv.stdout,
                               capture_output=True,
                               universal_newlines=True)

  for line in midicsv2ass.stdout.splitlines():
    line = line.strip()
    if not len(line): continue

    if re.match(re_blank, line):
      continue

    line = line.replace("\\blank", "")
    line = line.replace("{\\k0}", "")

    print(line)


if __name__ == "__main__":
  main()
