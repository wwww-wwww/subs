#!/usr/bin/env python3
import re

def parse_time(search):
  search = re.match(r"[\x20-\x7E]+", search).group()
  return sum([float(t) * 60**i for i, t in enumerate(search.split(":")[::-1])])

while True:
  x = input("time: ")
  if x.strip() == "q": exit()
  print(int(parse_time(x) * 1000000000))
