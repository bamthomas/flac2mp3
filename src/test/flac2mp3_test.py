# -*- coding: UTF-8 -*-
from struct import pack
import unittest
from flac2mp3 import get_mp3_filename, get_flac_tags
import multiprocessing
import flac2mp3

__author__ = 'bruno thomas'

class TestFlac2Mp3(unittest.TestCase):

    def test_get_flac_tags_one_comment(self):
        self.assertEquals({"TITRE" : "titre"}, get_flac_tags(vobis_block_header(1) + encode(b'TITRE=titre')))

    def test_get_flac_tags_two_comments_with_upper_and_lower_case(self):
        self.assertEquals({"TITRE" : "titre", "ALBUM" : "album"}, get_flac_tags(vobis_block_header(2) + encode('TiTrE=titre') + encode('album=album')))

    def test_get_flac_tags_two_comments_with_equal_sign_in_value(self):
        self.assertEquals({"TITRE" : "e=mc2", "ALBUM" : "album"}, get_flac_tags(vobis_block_header(2) + encode('TiTrE=e=mc2') + encode('album=album')))

    def test_get_flac_tags_two_comments_with_carriage_return(self):
        self.assertEquals({"DESCRIPTION" : u"Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino", "TITRE" : "titre"},
            get_flac_tags(vobis_block_header(2) + encode(u"DESCRIPTION=Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino") + encode(u"TITRE=titre")))

    def test_get_cpu_count(self):
        def raise_NotImplementedError(): raise NotImplementedError

        saved_cpu_count_func=multiprocessing.cpu_count
        try:
             self.assertEqual(multiprocessing.cpu_count(), flac2mp3.get_cpu_count())

             multiprocessing.cpu_count = raise_NotImplementedError
             self.assertEqual(1, flac2mp3.get_cpu_count())
        finally: multiprocessing.cpu_count = saved_cpu_count_func

    def test_get_mp3_dir(self):
        self.assertEquals('/target/dir/song.mp3', get_mp3_filename('/target', '/absolute/flac/path/', '/absolute/flac/path/dir/song.flac'))
        self.assertEquals('/target/dir/song.mp3', get_mp3_filename('/target', '/absolute/flac/path', '/absolute/flac/path/dir/song.flac'))

def vobis_block_header(nb_comments):
    return '\x06\x00\x00\x00' + b'vendor' + pack('I', nb_comments)

def encode(comment):
    return pack('I', len(comment)) + comment
