import os, subprocess, subs, prass, re, argparse, time, shutil
from ilock import ILock

attachments = ["LT.ttf", "LT_3italic.ttf"]

re_pos = r"(\\pos\(([0-9]+|[0-9]+\.[0-9]+), *([0-9]+|[0-9]+\.[0-9]+)\))"
re_move = r"(\\move\(([0-9\-,\.]+)\))"
re_clip = r"(\\clip\((.+)\))"

re_draw = r"\{.*?\\p[1-9][0-9]*.*?\}([^\{]+)"

re_tag = r"\{.*?\}"

re_simple = [
  (r"(\\fs([0-9]+\.[0-9]+|[0-9]+))", "\\fs{}"),
  (r"(\\bord([0-9]+\.[0-9]+|[0-9]+))", "\\bord{}"),
  (r"(\\xbord([0-9]+\.[0-9]+|[0-9]+))", "\\xbord{}"),
  (r"(\\ybord([0-9]+\.[0-9]+|[0-9]+))", "\\ybord{}"),
  (r"(\\shad([0-9]+\.[0-9]+|[0-9]+))", "\\shad{}"),
  (r"(\\xshad([0-9]+\.[0-9]+|[0-9]+))", "\\xshad{}"),
  (r"(\\yshad([0-9]+\.[0-9]+|[0-9]+))", "\\yshad{}"),
  (r"(\\blur([0-9]+\.[0-9]+|[0-9]+))", "\\blur{}"),
  (r"(\\be([0-9]+\.[0-9]+|[0-9]+))", "\\be{}"),
]

num = lambda n: round(n, 3) if n % 1 else int(n)


def scale(src, scale_width, scale_height):
  events = src._find_section(subs.EVENTS_SECTION)
  for event in events.events:
    matches = re.findall(re_draw, event.text)
    for match in matches:
      numbers = []
      for number in match.split(" "):
        try:
          numbers.append(num(float(number) * scale_height))
        except:
          numbers.append(number)
      numbers = [str(number) for number in numbers]
      scaled = " ".join(numbers)
      event.text = event.text.replace(match, scaled)

    groups = re.findall(re_tag, event.text)
    for group in groups:
      text = group

      matches = re.findall(re_pos, group)
      for match in matches:
        x = num(float(match[1]) * scale_width)
        y = num(float(match[2]) * scale_height)
        scaled_pos = f"\\pos({x},{y})"
        text = text.replace(match[0], scaled_pos)

      matches = re.findall(re_move, group)
      for match in matches:
        numbers = match[1].split(",")
        numbers = [num(float(number) * scale_height) for number in numbers]
        numbers = [str(number) for number in numbers]
        scaled = "\\move({})".format(",".join(numbers))
        text = text.replace(match[0], scaled)

      matches = re.findall(re_clip, group)
      for match in matches:
        numbers = []
        for number in match[1].split(" "):
          try:
            numbers.append(num(float(number) * scale_height))
          except:
            numbers.append(number)
        numbers = [str(number) for number in numbers]
        scaled = "\\clip({})".format(" ".join(numbers))
        text = text.replace(match[0], scaled)

      for r in re_simple:
        matches = re.findall(r[0], group)
        for match in matches:
          scaled_pos = r[1].format(num(float(match[1]) * scale_height))
          text = text.replace(match[0], scaled_pos)

      event.text = event.text.replace(group, text)


def proc(src, ref, out):
  src = prass.AssScript.from_ass_file(src)
  ref = prass.AssScript.from_ass_file(ref)

  src.append_styles(ref, False, True)

  from_width, from_height = src._find_section(
    subs.SCRIPT_INFO_SECTION).get_resolution()
  to_width, to_height = ref._find_section(
    subs.SCRIPT_INFO_SECTION).get_resolution()

  if from_width != to_width or from_height != to_height:
    scale_width = to_width / float(from_width)
    scale_height = to_height / float(from_height)
    scale(src, scale_width, scale_height)
    src.scale_to_reference(ref)

  src.cleanup(False, True, True, False, False, False, False)

  src.to_ass_file(out)


def apply(filename, only, style_source):
  if only and not any(s in filename.lower() for s in only.lower().split(";")):
    print("skipping", filename)
    return

  print("opening", filename)

  while True:
    try:
      open(filename).close()
      break
    except:
      time.sleep(1)

  ffmpeg = [
    "ffmpeg",
    "-hide_banner",
    "-y",
    "-i",
    filename,
    "-c:s",
    "copy",
    "-map",
    "0:s:0",
    "subs.ass",
  ]

  r = subprocess.run(ffmpeg,
                     stderr=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL)

  assert r.returncode == 0

  proc("subs.ass", style_source, "subs.ass")

  mkvmerge = [
    "mkvmerge",
    "-o",
    "tmp.mkv",
    "-S",
    filename,
    "--language",
    "0:eng",
    "subs.ass",
  ]

  for attachment in attachments:
    mkvmerge += ["--attach-file", attachment]

  r = subprocess.run(mkvmerge)

  assert r.returncode == 0

  os.remove(filename)
  os.remove("subs.ass")
  shutil.move("tmp.mkv", filename)


if __name__ == "__main__":
  os.chdir(os.path.dirname(os.path.abspath(__file__)))

  parser = argparse.ArgumentParser()
  parser.add_argument("--only", default=None)
  parser.add_argument("--style", default="style.ass")
  parser.add_argument("input")

  args = parser.parse_args()

  print("acquiring lock")
  with ILock("subs"):
    if os.path.isdir(args.input):
      print("directory", args.input)
      for filename in os.listdir(args.input):
        if os.path.splitext(filename)[1].lower() != ".mkv": continue
        path = os.path.join(args.input, filename)
        if os.path.isfile(path):
          apply(path, args.only, args.style)
    else:
      if os.path.splitext(args.input)[1].lower() == ".mkv":
        apply(args.input, args.only, args.style)
      else:
        print("input isnt mkv")
