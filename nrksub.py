#!/usr/bin/env python3

# nrksub
# Copyright (C) 2015 Jashandeep Sohi <jashandeep.s.sohi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Download, translate subtitles for NRK TV programs.
"""

import requests
import re
import bs4
import datetime
from argparse import ArgumentParser, FileType


__version__ = "0.4.0"

arg_parser = ArgumentParser(
  description = __doc__
)

arg_parser.add_argument(
  "url",
  help = "Program URL"
)

arg_parser.add_argument(
  "output",
  help = "Output file. Default is '-' (STDOUT).",
  type = FileType("w", encoding="utf-8"),
  nargs = "?",
  default = "-"
)

arg_parser.add_argument(
  "-f", "--format",
  help = "Output format. Can either be 'srt' or 'ttml'. Default is 'srt'.",
  choices = ["ttml", "srt"],
  default = "srt"
)

arg_parser.add_argument(
  "-l", "--lang",
  help = """
  Two letter language code for the language into which the original Norwegian
  subtitles should be translated using Google Translate. Default is 'en' for
  English. To skip the translation provide 'no' for Norwegian.
  """,
  default = "en"
)

arg_parser.add_argument(
  "-u", "--user-agent",
  help = "User Agent for HTTP Requests. Default is '%(default)s'.",
  default = "Mozilla/5.0 (X11; Linux x86_64; rv:37.0) Gecko/20100101 "
            "Firefox/37.0"
)

def str2td(s):
  """
  Convert a ``HH:MM:SS.millisec`` formated :obj:`str` to a
  :obj:`datetime.timedelta` object.
  """
  h, m, s = map(float, s.strip().split(":"))
  return datetime.timedelta(hours=h, minutes=m, seconds=s)

def td2str(td):
  """
  Convert a :obj:`datetime.timedelta` object to a ``HH:MM:SS.millisec``
  formated :obj:`str`.
  """
  h, h_r = divmod(td.total_seconds(), 3600)
  m, s = divmod(h_r, 60)
  return "{h:02.0f}:{m:02.0f}:{s:06.3f}".format(h=h, m=m, s=s)

def ttml2srt(ttml):
  """
  Convert a TTML :obj:`bs4.BeautifulSoup` object into SRT format.
  """
  f = lambda td: td2str(td).replace(".", ",")
  
  for i, p in enumerate(ttml.tt.body.div("p"), 1):
    begin = str2td(p["begin"])
    dur = str2td(p["dur"])
    end = begin + dur
    
    yield "{}\n{} --> {}\n".format(i, f(begin), f(end))
    
    for c in p.children:
      if c.name == "br":
        yield "\n"
      elif c.name == "span" and c["style"] == "italic":
        yield "<i>{}</i>".format(c.string.strip())
      elif c.string and c.string != "\n":
        yield c.string.strip()
      
      if c.next_sibling == None:
        yield "\n\n"
      
if __name__ == "__main__":

  args = arg_parser.parse_args()
  
  req_session = requests.Session()
  req_session.headers.update({
    "User-Agent": args.user_agent,
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  })
  
  program_resp = req_session.get(args.url)
  
  sub_id_match = re.search(
    """
    .*?data-subtitlesurl\s+=\s+['"]
    .*?programsubtitles/([a-zA-Z0-9]+)
    ["']
    """,
    program_resp.text,
    re.DOTALL|re.VERBOSE
  )
  if not sub_id_match:
    args.error("could not find subtitle id")
  
  sub_id = sub_id_match.group(1)
 
  ttml_resp = req_session.get(
    "http://tv.nrk.no/programsubtitles/{}".format(sub_id)
  )
  
  ttml = bs4.BeautifulSoup(ttml_resp.text, "html.parser")
    
  if args.lang != "no":
    nav_strings = ttml.tt.body.div.find_all(text=True)
    trans_resp = req_session.post(
      "https://translate.googleusercontent.com/translate_f",
      files = {"file": ("trans.txt", "\r\r".join(nav_strings), "text/plain")},
      data = {
        "sl": 'no',
        "tl": args.lang,
        "js": 'y',
        "prev": "_t",
        "hl": "en",
        "ie": "UTF-8",
        "edit-text": "",
      },
      headers = {"Referer": "https://translate.google.com/"}
    )
    trans_soup = bs4.BeautifulSoup(trans_resp.text, "html.parser")
    
    trans_strings = trans_soup.pre.string.split("\r\r")
    
    assert len(nav_strings) == len(trans_strings)
    
    for i, trans in enumerate(trans_strings):
      nav_strings[i].replace_with(trans)
    
    ttml.tt["lang"] = args.lang
  
  if args.format == "srt":
    for line in ttml2srt(ttml):
      args.output.write(str(line))
  else:
    ttml.tt.insert(0, ttml.new_string("Created using nrksub", bs4.Comment))  
    args.output.write(ttml.prettify() + "\n")
  
# vim: tabstop=2 expandtab
