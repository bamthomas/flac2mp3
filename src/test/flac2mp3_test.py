# -*- coding: UTF-8 -*-
import unittest
from flac2mp3 import read_meta_flac, get_mp3_filename, transcode

__author__ = 'bruno thomas'

class TestFlac2Mp3(unittest.TestCase):
    def test_read_metaflac_one_line(self):
        self.assertEquals({"TITRE" : "titre"}, read_meta_flac("TITRE=titre"))

    def test_read_meta_flac_two_lines(self):
        self.assertEquals({"TITRE" : "titre", "ALBUM" : "album"}, read_meta_flac("TITRE=titre\nALBUM=album"))

    def test_read_meta_flac_two_lines_with_upper_and_lower_case(self):
        self.assertEquals({"TITRE" : "titre", "ALBUM" : "album"}, read_meta_flac("TiTrE=titre\nalbum=album"))

    def test_read_meta_flac_two_lines_with_carriage_return(self):
        self.assertEquals({"DESCRIPTION" : u"Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino", "TITRE" : "titre"},
            read_meta_flac(u"DESCRIPTION=Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino\nTITRE=titre"))

    def test_get_mp3_dir(self):
        self.assertEquals('/target/dir/song.mp3', get_mp3_filename('/target', '/absolute/flac/path/', '/absolute/flac/path/dir/song.flac'))
        self.assertEquals('/target/dir/song.mp3', get_mp3_filename('/target', '/absolute/flac/path', '/absolute/flac/path/dir/song.flac'))
