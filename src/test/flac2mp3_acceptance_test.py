# -*- coding: UTF-8 -*-
import subprocess
from os.path import dirname, getsize
import unittest
import binascii
import eyeD3
from flac2mp3_test import Flac2Mp3, LAME_COMMAND

__author__ = 'bruno thomas'


class TestFlac2Mp3Acceptance(unittest.TestCase):
    def test_recette(self):
        self.cree_fichier_flac('/tmp/tmp.flac')

        Flac2Mp3().run('/tmp/tmp.flac','/tmp')

        tag = eyeD3.Tag()
        tag.link('/tmp/tmp.mp3')
        self.assertEquals(u"artist", tag.getArtist())
        self.assertEquals((1,15), tag.getTrackNum())
        self.assertEquals(u"album", tag.getAlbum())
        self.assertEquals(u"title", tag.getTitle())
        self.assertEquals('Electronic', tag.getGenre().getName())
        self.assertEquals('2008', (tag.getDate()[0]).getYear())


    def cree_fichier_flac(self, flac_file):
        with open('/tmp/tmp.wav', 'wb') as mp3:
            mp3.write(binascii.a2b_hex("524946462408000057415645666d7420100000000100020022560000885801000400100064617461000800000000000024171ef33c133c1416f918f934e723a63cf224f211ce1a0d"))

        open(dirname(flac_file) + "/cover.jpg", 'w').close()

        flac_cmde = u'/usr/bin/flac -V --totally-silent -f -T ARTIST=artist -T TRACKNUMBER=1 -T TRACKTOTAL=15 -T ALBUM=album -T TITLE=title -T GENRE=Electronic -T DATE=2008 /tmp/tmp.wav -o %s' % flac_file
        subprocess.call(flac_cmde.split(' '))