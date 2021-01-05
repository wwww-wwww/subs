#!/usr/bin/env python3
import sys, os, argparse
from fontTools import ttLib

parser = argparse.ArgumentParser()
parser.add_argument("font")
parser.add_argument("name")
parser.add_argument("-o", "--output", help="Output file")

args = parser.parse_args()

tt = ttLib.TTFont(args.font)

style = None
for record in tt["name"].names:
  if record.nameID == 2:
    style = str(record)
    break

assert style

nameID1_string = args.name
nameID16_string = args.name
nameID4_string = f"{args.name} {style}"
nameID6_string = f"{args.name.replace(' ', '')}-{style.replace(' ', '')}"

for record in tt["name"].names:
  if record.nameID == 1:
    record.string = nameID1_string
  elif record.nameID == 4:
    record.string = nameID4_string
  elif record.nameID == 6:
    record.string = nameID6_string
  elif record.nameID == 16:
    record.string = nameID16_string

tt.save(args.output or args.font)
print("saved", nameID4_string, "to", args.output or args.font)
