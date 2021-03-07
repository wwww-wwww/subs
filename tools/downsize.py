#!/usr/bin/env python3
import argparse, fontforge, sys


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("font")
  parser.add_argument("name")
  parser.add_argument("out")

  args = parser.parse_args()

  font = fontforge.open(args.font)

  sys.stdin.reconfigure(encoding="utf-8")
  for i in sys.stdin.read():
    font.selection[ord(i)] = True

  font.selection.invert()

  for i in font.selection.byGlyphs:
    font.removeGlyph(i)

  postscript_font_name = args.name.replace(" ", "")

  style = None

  for s in font.sfnt_names:
    if s[1] == "SubFamily":
      style = s[2]
      break

  assert style

  font.familyname = args.name
  font.fullname = f"{postscript_font_name}-{style.replace(' ', '')}"
  font.fontname = f"{postscript_font_name}-{style.replace(' ', '')}"

  font.generate(args.out)
  print("saved to", args.out)


if __name__ == "__main__":
  main()
