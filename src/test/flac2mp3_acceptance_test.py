# -*- coding: UTF-8 -*-
from os.path import join
import shutil
import subprocess
from tempfile import mkdtemp
from os.path import dirname, isdir
from os import makedirs
import unittest
import binascii
import eyeD3
from flac2mp3_test import Flac2Mp3

__author__ = 'bruno thomas'


class TestFlac2Mp3Acceptance(unittest.TestCase):
    def test_recette(self):
        self.cree_fichier_flac('/tmp/tmp.flac')

        Flac2Mp3().transcode('/tmp/tmp.flac','/tmp/tmp.mp3')

        tag = eyeD3.Tag()
        tag.link('/tmp/tmp.mp3')
        self.assertEquals(u"artist", tag.getArtist())
        self.assertEquals((1,15), tag.getTrackNum())
        self.assertEquals(u"album!", tag.getAlbum())
        self.assertEquals(u"title", tag.getTitle())
        self.assertEquals('Electronic', tag.getGenre().getName())
        self.assertEquals('2008', (tag.getDate()[0]).getYear())

    def test_trouve_fichiers_flac(self):
        tmp = mkdtemp()
        try:
            for dir in ('/r1', '/r2/r21', '/r3'):
                if not isdir(tmp + dir):
                    makedirs(tmp + dir)
            for file in ('/r1/f11.flac', '/r1/f12.flac', '/r2/r21/f21.flac'): open(tmp + file, 'w').close()
            liste_attendue = [tmp + '/r1/f11.flac', tmp + '/r1/f12.flac', tmp + '/r2/r21/f21.flac']

            self.assertItemsEqual(liste_attendue, list(Flac2Mp3().trouve_fichiers(".flac", tmp)))
            self.assertItemsEqual(liste_attendue, list(Flac2Mp3().trouve_fichiers(".flac", tmp + "/r1", tmp + "/r2")))
        finally:
            shutil.rmtree(tmp)

    def test_convert_arborescence(self):
        tmp = mkdtemp()
        try:
            for dir in ('/r1', '/r2/r21', '/r3', '/mp3'):
                if not isdir(tmp + dir):
                    makedirs(tmp + dir)
            self.cree_fichier_flac(join(tmp, 'r1/f11.flac'))
            self.cree_fichier_flac(join(tmp, 'r1/f12.flac'))
            self.cree_fichier_flac(join(tmp, 'r2/r21/f21.flac'))

            Flac2Mp3().run(join(tmp, 'mp3'), tmp, tmp)

            self.assertItemsEqual([join(tmp,mp3) for mp3 in ("mp3/r1/f11.mp3", "mp3/r1/f12.mp3", "mp3/r2/r21/f21.mp3")],
                list(Flac2Mp3().trouve_fichiers(".mp3", tmp)))

        finally:
            shutil.rmtree(tmp)

    def cree_fichier_flac(self, flac_file):
        with open('/tmp/tmp.wav', 'wb') as mp3:
            mp3.write(binascii.a2b_hex("524946462408000057415645666d7420100000000100020022560000885801000400100064617461000800000000000024171ef33c133c1416f918f934e723a63cf224f211ce1a0d"))

        open(dirname(flac_file) + "/cover.jpg", 'w').close()

        flac_cmde = u'/usr/bin/flac -V --totally-silent -f -T ARTIST=artist -T TRACKNUMBER=1 -T TRACKTOTAL=15 -T ALBUM=album! -T TITLE=title -T GENRE=Electronic -T DATE=2008 /tmp/tmp.wav -o %s' % flac_file
        subprocess.call(flac_cmde.split(' '))