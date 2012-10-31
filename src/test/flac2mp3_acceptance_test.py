# -*- coding: UTF-8 -*-
import shutil
import tempfile
from flac2mp3 import find_files, run, transcode, which, VobisCommentParser, CoverFile
import flac2mp3
import os
from os.path import join
import subprocess
from os.path import dirname, isdir
from os import makedirs
import unittest
import binascii
import eyeD3

__author__ = 'bruno thomas'

class TestFlac2Mp3Acceptance(unittest.TestCase):
    def init_files(self, tmp, embbed=False):
        flac_file = join(tmp, 'tmp.flac')
        self.create_flac_file(flac_file, embbed=embbed)
        return flac_file, join(tmp, 'tmp.mp3')

    def test_acceptance_one_file(self):
        with TemporaryDirectory() as tmp:
            flac_file, mp3_file = self.init_files(tmp)

            transcode(flac_file, mp3_file)

            tag = eyeD3.Tag()
            tag.link(mp3_file)
            self.assertEquals(u"artist", tag.getArtist())
            self.assertEquals((1,15), tag.getTrackNum())
            self.assertEquals(u"album", tag.getAlbum())
            self.assertEquals(u"title", tag.getTitle())
            self.assertEquals('description', tag.getComments()[0].comment)
            self.assertEquals('Electronic', tag.getGenre().getName())
            self.assertEquals('2008', (tag.getDate()[0]).getYear())
            self.assertEquals(1, len(tag.getImages()))

    def test_target_mp3_exists_flac_is_not_transcoded_again(self):
        with TemporaryDirectory() as tmp, CountingTranscodeCalls() as transcode:
            flac_file, mp3_file = self.init_files(tmp)

            flac2mp3.process_transcoding((flac_file, tmp, tmp))
            flac2mp3.process_transcoding((flac_file, tmp, tmp))

            self.assertEquals(1, transcode.count())

    def test_target_mp3_exists_with_differents_tags_flac_is_transcoded_again(self):
        with TemporaryDirectory() as tmp, CountingTranscodeCalls() as transcode:
            flac_file, mp3_file = self.init_files(tmp)

            flac2mp3.process_transcoding((flac_file, tmp, tmp))
            self.create_flac_file(flac_file, tags={'ARTIST': 'artist'})
            flac2mp3.process_transcoding((flac_file, tmp, tmp))

            self.assertEquals(2, transcode.count())

    def test_acceptance_one_file_with_embedded_cover(self):
        with TemporaryDirectory() as tmp:
            flac_file, mp3_file = self.init_files(tmp, embbed=True)

            transcode(flac_file, mp3_file)

            tag = eyeD3.Tag()
            tag.link(mp3_file)
            self.assertEquals(1, len(tag.getImages()))
            
            tmp_file_pattern = '%s.*\%s' % (CoverFile.tmp_prefix, CoverFile.tmp_suffix)
            self.assertEquals(0, len(set(find_files(tmp_file_pattern, tempfile.gettempdir()))))

    def test_acceptance_one_file_with_spaces(self):
        with TemporaryDirectory() as tmp:
            flac_file = join(tmp, 'file with spaces.flac')
            mp3_file = join(tmp, 'file with spaces.mp3')
            self.create_flac_file(flac_file)

            transcode(flac_file, mp3_file)

            self.assertTrue(os.path.isfile(mp3_file))

    def test_one_file_one_tag(self):
        self.assert_tag_present_in_mp3('getArtist', 'ARTIST', 'artist')
        self.assert_tag_present_in_mp3('getTitle', 'TITLE', 'title')
        self.assert_tag_present_in_mp3('getAlbum', 'ALBUM', 'album')

    def test_one_file_one_tag_with_bash_special_chars(self):
        self.assert_tag_present_in_mp3('getArtist', 'ARTIST', '!!! money $ stars * and percentages %')

    def test_one_file_one_tag_with_accent(self):
        self.assert_tag_present_in_mp3('getArtist', 'ARTIST', u'titre à accent')

    def test_transcode_without_cover(self):
        with TemporaryDirectory() as tmp:
            self.create_flac_file(join(tmp, 'tmp.flac'), cover=None)
            transcode(join(tmp, 'tmp.flac'),join(tmp, 'tmp.mp3'))
            self.assertTrue(os.path.isfile(join(tmp, 'tmp.mp3')))

    def test_get_flac_tags(self):
        with TemporaryDirectory() as tmp:
            self.create_flac_file(join(tmp, 'tmp.flac'))

            parser = VobisCommentParser().parse(join(tmp, 'tmp.flac'))

            self.assertEquals({'ALBUM': 'album', 'TITLE': 'title', 'ARTIST': 'artist', 'TRACKTOTAL': '15', 'DATE': '2008',
                               'DESCRIPTION': 'description', 'GENRE': 'Electronic', 'TRACKNUMBER': '1', 'COPYRIGHT': 'copyright'},
                parser.flac_tags)

    def test_find_flac_files(self):
        with TemporaryDirectory() as tmp:
            for dir in ('/r1', '/r2/r21', '/r3'):
                if not isdir(tmp + dir):
                    makedirs(tmp + dir)
            for file in ('/r1/f11.flac', '/r1/f12.flac', '/r2/r21/f21.flac'): open(tmp + file, 'w').close()
            liste_attendue = [tmp + '/r1/f11.flac', tmp + '/r1/f12.flac', tmp + '/r2/r21/f21.flac']

            self.assertItemsEqual(liste_attendue, list(find_files(".*\.flac", tmp)))
            self.assertItemsEqual(liste_attendue, list(find_files(".*\.flac", tmp + "/r1", tmp + "/r2")))

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
            actual = list(find_files(".*.mp3", tmp))

            self.assertItemsEqual(actual, expected)

    def test_which(self):
        self.assertEquals('/bin/ls', which('ls'))
        self.assertEquals('/bin/ls', which('/bin/ls'))
        self.assertIsNone(which('blahblah'))

    def assert_tag_present_in_mp3(self, eyed3_method_name, flac_key, flac_value):
        with TemporaryDirectory() as tmp:
            flac_file = join(tmp, 'tmp.flac')
            mp3_file = join(tmp, 'tmp.mp3')
            self.create_flac_file(flac_file, tags={flac_key: flac_value})
            transcode(flac_file, mp3_file)
            tag = eyeD3.Tag()
            tag.link(mp3_file)
            self.assertEquals(flac_value, getattr(tag, eyed3_method_name)())

    def create_flac_file(self, flac_file, tags={'ARTIST':'artist', 'TRACKNUMBER': '1', 'TRACKTOTAL': '15', 'ALBUM': 'album', 'TITLE': 'title', 'GENRE': 'Electronic', 'DATE': '2008', 'DESCRIPTION': 'description','COPYRIGHT': 'copyright'}, cover='cover.jpg', embbed=False):
        with open('/tmp/tmp.wav', 'wb') as mp3:
            mp3.write(binascii.a2b_hex("524946462408000057415645666d7420100000000100020022560000885801000400100064617461000800000000000024171ef33c133c1416f918f934e723a63cf224f211ce1a0d"))

        command_tags = list()
        for (k,v) in tags.iteritems():
            command_tags.append('-T')
            command_tags.append('%s=%s' % (k,v))
        cover_path = None
        if cover:
            cover_path = join(dirname(flac_file), cover)
            with open(cover_path, 'w') as jpg:
                jpg.write(binascii.a2b_hex('FFD8FFE000104A464946'))
            if embbed:
                command_tags.append('--picture=|image/jpeg||1x1x24/173|%s' % cover_path)

        flac_cmde = '/usr/bin/flac -V --totally-silent -f'.split(' ') + '/tmp/tmp.wav -o'.split(' ') + [flac_file]  + command_tags
        subprocess.call(flac_cmde)

        if cover and embbed :
            os.remove(cover_path)


class TemporaryDirectory(object):
    def __enter__(self):
        self.tempdir = tempfile.mkdtemp()
        return self.tempdir
    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.tempdir, ignore_errors = True)

class CountingTranscodeCalls(object):
    def __init__(self):
        self.nb_transcode = [0]
    def __enter__(self):
        self.transcode_func = flac2mp3.transcode
        flac2mp3.transcode = self.transcode_and_count
        return self

    def __exit__(self, type, value, traceback):
        flac2mp3.transcode = self.transcode_func

    def transcode_and_count(self, flac_file, mp3_file):
        self.transcode_func(flac_file, mp3_file)
        self.nb_transcode[0] += 1

    def count(self):
        return self.nb_transcode[0]