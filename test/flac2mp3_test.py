# -*- coding: UTF-8 -*-
from struct import pack
import unittest
from flac2mp3 import get_mp3_filename, VobisCommentParser, get_cpu_count
import multiprocessing

__author__ = 'bruno thomas'


class TestFlac2Mp3(unittest.TestCase):

    def test_get_flac_tags_one_comment(self):
        tags = VobisCommentParser().get_flac_tags(vobis_block_header(1) + encode(b'TITRE=titre'))
        self.assertEqual({'TITRE': 'titre'}, tags)

    def test_get_flac_tags_two_comments_with_upper_and_lower_case(self):
        tags = VobisCommentParser().get_flac_tags(vobis_block_header(2) + encode(b'TiTrE=titre') + encode(b'album=album'))
        self.assertEqual({'TITRE': 'titre', 'ALBUM': 'album'}, tags)

    def test_get_flac_tags_two_comments_with_equal_sign_in_value(self):
        tags = VobisCommentParser().get_flac_tags(vobis_block_header(2) + encode(b'TiTrE=e=mc2') + encode(b'album=album'))
        self.assertEqual({'TITRE': 'e=mc2', 'ALBUM': 'album'}, tags)

    def test_get_flac_tags_unicode_strings_for_artist_album_title(self):
            tags = VobisCommentParser().get_flac_tags(vobis_block_header(3) + encode('title=à'.encode()) + encode('album=bé'.encode()) + encode('artist=cè'.encode()))
            self.assertEqual({'TITLE': 'à', 'ALBUM': 'bé', 'ARTIST': 'cè'}, tags)

    def test_get_flac_tags_two_comments_with_carriage_return(self):
        tags = VobisCommentParser().get_flac_tags(vobis_block_header(2) + encode(
            'DESCRIPTION=Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino'.encode()) + encode('TITRE=titre'.encode()))
        self.assertEqual({'DESCRIPTION': 'Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino', 'TITRE' : 'titre'}, tags)

    def test_get_cpu_count(self):
        def raise_NotImplementedError(): raise NotImplementedError

        saved_cpu_count_func=multiprocessing.cpu_count
        try:
             self.assertEqual(multiprocessing.cpu_count(), get_cpu_count())

             multiprocessing.cpu_count = raise_NotImplementedError
             self.assertEqual(1, get_cpu_count())
        finally:
            multiprocessing.cpu_count = saved_cpu_count_func

    def test_get_mp3_dir(self):
        self.assertEqual('/target/dir/song.mp3', get_mp3_filename('/target', '/absolute/flac/path/', '/absolute/flac/path/dir/song.flac'))
        self.assertEqual('/target/dir/song.mp3', get_mp3_filename('/target', '/absolute/flac/path', '/absolute/flac/path/dir/song.flac'))


def vobis_block_header(nb_comments):
    return b'\x06\x00\x00\x00' + b'vendor' + pack('I', nb_comments)


def encode(comment):
    return pack('I', len(comment)) + comment
