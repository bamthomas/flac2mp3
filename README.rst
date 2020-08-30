|Build Status|

Description
===========

This is a utility script for transcoding flac files
into mp3 files keeping covers, tags, and directory structure. It is
multithreaded and creates as much thread as the number of cores on the
host.

The flac tags will be added to the mp3 files ut8 encoded, and if a
cover.jpg file is found in the flac files directory it will be added to
the mp3.

| The mp3 generated will be itunes compliant (accents, covers) and encoded with lame command :

::

    lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100

Why another flac2mp3 command ?
==============================

Because I didn't find one that included the cover and that did not break my accents on itunes. Cf http://www.barreverte.fr/ou-sont-mes-accents-dans-itunes (sorry, in french).

Second because I wanted it to be robust (for example with comments on multiple lines, shell caracters in tags like ``!*$``) and unit tested.

Compatibility and dependencies
==============================

It has been tested with linux (with python version >= 2.6.2), MacOS (>=
Snow Leopard), Windows Vista (with python version >= 2.6.2).

Depends on ``lame`` (>=3.99 if you want your accents) and ``flac`` for
the runtime.

Depends on ``eyeD3`` for unit testing and developing.

Lame
----

Is a well known tool for encoding mp3 files. You can dowload and compile
the code from the lame site : http://lame.sourceforge.net/

Binaries bundles can be found for mac and windows :
http://rarewares.org/mp3-lame-bundle.php

Flac
----

Is a free and open lossless audio codec. There are links to dowload
pages in the official site : http://flac.sourceforge.net/download.html

Usage
=====

``flac2mp3 [origin directories] mp3/repository/destination``

-  If one argument is given it is the destination : it will transcode
   flac files found under the current directory and put mp3 files in the
   destination directory with the same directory structure.
-  If more than one argument is given, it will transcode flac files from
   the given directories to the destination.

for example, if you have :

::

    /path/to/flac/artist1/album1/song1.flac
                 |              |song2.flac
                 |              |song3.flac
                 |              |cover.jpg
                 |
                 /artist2/album1/song1.flac
                                |song2.flac
                                |cover.jpg

1) if you do in flac directory :

::

    $ flac2mp3.py ../mp3

you'll have :

::

    /path/to/flac/artist1/album1/song1.flac
            |    |              |song2.flac
            |    |              |song3.flac
            |    |              |cover.jpg
            |    |
            |    /artist2/album1/song1.flac
            |                   |song2.flac
            |                   |cover.jpg
            |
            /mp3/artist1/album1/song1.mp3
                |              |song2.mp3
                |              |song3.mp3
                |
                /artist2/album1/song1.mp3
                               |song2.mp3

2) if you do in flac directory :

::

    $ flac2mp3.py artist2 ../mp3

you'll have :

::

    /path/to/flac/artist1/album1/song1.flac
            |    |              |song2.flac
            |    |              |song3.flac
            |    |
            |    /artist2/album1/song1.flac
            |                   |song2.flac
            |
            /mp3/artist2/album1/song1.mp3
                               |song2.mp3

This is a work in progress.

Development
===========

To develop and test, use your favorite IDE (mine is pycharm).

With bash, to run the tests you can do :

::

    $ virtualenv venv
    $ source venv/bin/activate
    $ python setup.py develop
    $ pip install -e ".[dev]"
    $ nosetests

To release :

::

    $ python setup.py sdist bdist_egg upload

Known issues
============

-  [windows] weird errors when deleting temp cover images embedded in
   flac files on windows : "WindowsError: [Error 32] The process cannot
   access the file because it is being used by another process". But the
   transcoding is ok anyway.
-  [all] the skip file function is not working after windows encoding
   stuffs
-  [windows] the log for each track start encoding is not displayed

.. |Build Status| image:: https://travis-ci.org/bamthomas/flac2mp3.png
   :target: https://travis-ci.org/bamthomas/flac2mp3