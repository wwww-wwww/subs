#!/usr/bin/env python3
# Usage with downsize.py and fontforge:
# asstext.py SUBTITLE_FILE text FONTNAME | ffpython downsize.py FONT_FILE NEW_FONTNAME OUTPUT.otf
#
# Usage with pytfsubset:
# asstext.py SUBTITLE_FILE text FONTNAME > characters
# pyftsubset FONT --text-file=characters --output-file=OUTPUT.otf
import re, sys, argparse
from collections import namedtuple, defaultdict


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("subtitles")
  command_arg = parser.add_argument("command", help="fonts text")

  args = parser.parse_args(sys.argv[1:3])

  if args.command not in ["fonts", "text"]:
    parser.error(
      f"Unsupported command {args.command}\nAvailable commands: fonts text")

  with open(args.subtitles, "r", encoding="utf-8") as f:
    lines = f.readlines()

  fonts = defaultdict(list)
  styles = {}
  for line in lines:
    if line.startswith("Style: "):
      line = line[7:].strip()
      line = line.split(",")
      style = line[0]
      font = line[1]
      if font[0] == "@":
        font = font[1:]
      styles[style] = font
    elif line.startswith("Dialogue: "):
      line = line[10:].strip()
      line = line.split(",")

      style = line[3]

      text = ",".join(line[9:])
      text = re.sub(r"{((?!\\fn.+?}).)+?}", "", text)  # remove tags

      selected_font = styles[style]
      while len(text) > 0:
        text = re.sub(r"{((?!\\fn).)+?}", "", text)
        r = re.search(r"{\\fn(.+?)}", text)
        if r:
          fonts[selected_font].append(text[:r.start()])
          text = text[r.end():]
          selected_font = r.group(1)
        else:
          fonts[selected_font].append(text)
          break

  if args.command == "fonts":
    [print(font) for font in fonts]

  if args.command == "text":
    font = " ".join(sys.argv[3:])
    if not font:
      print("font name unspecified")
      exit(1)

    if font not in fonts:
      print("font not found")
      exit(1)

    text = "".join(fonts[font])
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write("".join(sorted(list(set(text)))))


if __name__ == "__main__":
  main()
