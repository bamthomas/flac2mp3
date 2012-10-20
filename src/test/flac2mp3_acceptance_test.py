# -*- coding: UTF-8 -*-
import shutil
import tempfile
from flac2mp3 import find_files, run, transcode, get_flac_tags, get_vobis_comment_bloc, which
from os.path import join
import subprocess
from os.path import dirname, isdir
from os import makedirs
import unittest
import binascii
import eyeD3

__author__ = 'bruno thomas'



class TestFlac2Mp3Acceptance(unittest.TestCase):
    def test_acceptance_one_file(self):
        self.create_flac_file('/tmp/tmp.flac')

        transcode('/tmp/tmp.flac','/tmp/tmp.mp3')

        tag = eyeD3.Tag()
        tag.link('/tmp/tmp.mp3')
        self.assertEquals(u"artist", tag.getArtist())
        self.assertEquals((1,15), tag.getTrackNum())
        self.assertEquals(u"album!", tag.getAlbum())
        self.assertEquals(u"title", tag.getTitle())
        self.assertEquals('description', tag.getComments()[0].comment)
        self.assertEquals('Electronic', tag.getGenre().getName())
        self.assertEquals('2008', (tag.getDate()[0]).getYear())

    def test_get_flac_tags(self):
        self.create_flac_file('/tmp/tmp.flac')
        self.assertEquals({'ALBUM': 'album!', 'TITLE': 'title', 'ARTIST': 'artist', 'TRACKTOTAL': '15', 'DATE': '2008', 'DESCRIPTION': 'description', 'GENRE': 'Electronic', 'TRACKNUMBER': '1'},
            get_flac_tags(get_vobis_comment_bloc('/tmp/tmp.flac')))

    def test_find_flac_files(self):
        with TemporaryDirectory() as tmp:
            for dir in ('/r1', '/r2/r21', '/r3'):
                if not isdir(tmp + dir):
                    makedirs(tmp + dir)
            for file in ('/r1/f11.flac', '/r1/f12.flac', '/r2/r21/f21.flac'): open(tmp + file, 'w').close()
            liste_attendue = [tmp + '/r1/f11.flac', tmp + '/r1/f12.flac', tmp + '/r2/r21/f21.flac']

            self.assertItemsEqual(liste_attendue, list(find_files(".flac", tmp)))
            self.assertItemsEqual(liste_attendue, list(find_files(".flac", tmp + "/r1", tmp + "/r2")))

    def test_convert_tree(self):
        with TemporaryDirectory() as tmp:
            for dir in ('/r1', '/r2/r21', '/r3', '/mp3'):
                if not isdir(tmp + dir):
                    makedirs(tmp + dir)
            self.create_flac_file(join(tmp, 'r1/f11.flac'))
            self.create_flac_file(join(tmp, 'r1/f12.flac'))
            self.create_flac_file(join(tmp, 'r2/r21/f21.flac'))

            run(join(tmp, 'mp3'), tmp, tmp)

            expected = (join(tmp, mp3) for mp3 in ("mp3/r1/f11.mp3", "mp3/r1/f12.mp3", "mp3/r2/r21/f21.mp3"))
            actual = list(find_files(".mp3", tmp))

            self.assertItemsEqual(actual, expected)

    def test_which(self):
        self.assertEquals('/bin/ls', which('ls'))
        self.assertIsNone(which('blahblah'))

    def create_flac_file(self, flac_file):
        with open('/tmp/tmp.wav', 'wb') as mp3:
            mp3.write(binascii.a2b_hex("524946462408000057415645666d7420100000000100020022560000885801000400100064617461000800000000000024171ef33c133c1416f918f934e723a63cf224f211ce1a0d"))

        open(dirname(flac_file) + "/cover.jpg", 'w').close()

        flac_cmde = u'/usr/bin/flac -V --totally-silent -f -T ARTIST=artist -T TRACKNUMBER=1 -T TRACKTOTAL=15 -T ALBUM=album! -T TITLE=title -T GENRE=Electronic -T DATE=2008 -T DESCRIPTION=description /tmp/tmp.wav -o %s' % flac_file
        subprocess.call(flac_cmde.split(' '))


class TemporaryDirectory(object):
    def __enter__(self):
        self.tempdir = tempfile.mkdtemp()
        return self.tempdir
    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.tempdir, ignore_errors = True)
