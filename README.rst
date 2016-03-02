nrksub
======
Download, translate subtitles for NRK TV programs.

Dependencies
------------
- Python 3.4+
- Beautiful Soup 4
- Requests

Usage
-----
To download subtitles for a programs, provide it's URL as the first argument::

 $ url='https://tv.nrk.no/serie/side-om-side/MUHH48000415/sesong-3/episode-4'
 $ nrksub.py $url

Help
****
All command line options and arguments, and their purposes can be queried using
the help switch::

 $ nrksub.py --help

File
****
By default, nrksub will print the subtitles out to STDOUT. To write to a file,
provide a file name as the second argument::

 $ nrksub.py $url nytt-paa-nytt-26-12-2014.srt

Translate
*********
nrksub can translate the Norwegian subtitles provided by NRK automatically using
Google Translate. The translations are by no means perfect, but they are better
than nothing. By default, the subtitles are translated to English, but you can
use any language supported by Google Translate::

 $ nrksub.py --lang es $url
 Spanish output
 $ nrksub.py --lang de $url
 German output

If you want the original Norwegian subtitles, set the language to ``no``
(for Norwegian). This will skip the translation process::

 $ nrksub.py --lang no $url

Format
******
By default, nrksub will output SRT format subtitles. nrksub can also output
TTML format subtitles, but this is mostly for debugging purposes and of little
use, as rarely any video player supports them::

 $ nrksub.py --format ttml $url

More formats maybe added in the future, if I have the time.

.. vim: tabstop=1 expandtab
