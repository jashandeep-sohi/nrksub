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

import requests
import bs4
import datetime
from argparse import ArgumentParser, FileType

"""
Download, convert subtitles for NRK TV (tv.nrk.no) programmes.
"""

arg_parser = ArgumentParser(
  description = __doc__
)

arg_parser.add_argument(
  "id",
  help = "Program ID (e.g. MUHH02001815)"
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
  help = "Output format. Currently, only 'ttml' is supported. "
         "Default is 'ttml'.",
  choices = ["ttml",],
  default = "srt"
)

arg_parser.add_argument(
  "-l", "--lang",
  help = "Two letter language code for the language into which the original "
         "Norwegian subtitles should be translated using Google Translate. "
         "Default is 'en' for English. To skip the translation "
         "provide 'no' for Norwegian.",
  default = "en"
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
  Convert a :obj:`datetime.timedelta` object to a ``HH:MM:SS,millisec``
  formated :obj:`str` (note the comma).
  """
  h, h_r = divmod(td.total_seconds(), 3600)
  m, s = divmod(h_r, 60)
  return "{h:02.0f}:{m:02.0f}:{s:06.3f}".format(h=h, m=m, s=s).replace(".", ",")

if __name__ == "__main__":

  args = arg_parser.parse_args()
  
  req_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:37.0) Gecko/20100101 "
                  "Firefox/37.0",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer":	"https://translate.google.com/",
  }
  
  ttml_resp = requests.get(
    "http://tv.nrk.no/programsubtitles/{}".format(args.id),
    headers = req_headers
  )
  
  ttml = bs4.BeautifulSoup(ttml_resp.text, "html.parser")
    
  if args.lang != "no":
    nav_strings = ttml.tt.body.div.find_all(text=True)
    trans_resp = requests.post(
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
      headers = req_headers
    )
    translated = trans_resp.text.lstrip("<pre>").rstrip("</pre>").split("\r\r")
    
    for i, trans in enumerate(translated):
      nav_strings[i].replace_with(trans)
      
    ttml.tt["lang"] = args.lang
  
  ttml.tt.insert(0, ttml.new_string("Created using nrksub", bs4.Comment))  
  args.output.write(ttml.prettify() + "\n")
  
# vim: tabstop=2 expandtab
