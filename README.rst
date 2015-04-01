nrksub
======
Download, convert subtitles for NRK TV (tv.nrk.no) programmes.

Dependencies
------------
- Python 3.4+
- Beautiful Soup 4
- Requests

Usage
-----
To download subtitles for a programme, you first need to figure out the
programme ID. This can be easily extracted from the programme URL. For example,
the ID for this programme,
``http://tv.nrk.no/serie/nytt-paa-nytt/MUHH29005014/26-12-2014``, is
``MUHH29005014``.

Provide this ID to nrksub as the first argument to fetch the subtitles::

 $ ./nrksub.py MUHH29005014

Help
****
All command line options and arguments, and their purposes can be queried using
the help switch::

 $ ./nrksub.py --help

File
****
By default, nrksub will print the subtitles out to STDOUT. To write to a file,
provide a file name as the second argument::

 $ ./nrksub.py MUHH29005014 nytt-paa-nytt-26-12-2014.srt

Translate
*********
nrksub can translate the Norwegian subtitles provided by NRK automatically using
Google Translate. The translations are by no means perfect, but they are better
than nothing. By default, the subtitles are translated to English, but you can
use any language supported by Google Translate::

 $ ./nrksub.py --lang es MUHH29005014
 Spanish output
 $ ./nrksub.py --lang de MUHH29005014
 German output

If you want the original Norwegian subtitles, set the language to ``no``
(for Norwegian). This will skip the translation process::

 $ ./nrksub.py --lang no MUHH29005014

Format
******
By default, nrksub will output SRT format subtitles. nrksub can also output
TTML format subtitles, but this is mostly for debugging purposes and of little
use, as rarely any video player supports them::

 $ ./nrksub.py --format ttml MUHH29005014

More formats maybe added in the future, if I have the time.

.. vim: tabstop=1 expandtab
