# -*- coding: UTF-8 -*-
import commands
from genericpath import isdir
import os
from os.path import dirname, join
from subprocess import call
import unittest
import eyeD3
from eyeD3.frames import ImageFrame

LAME_COMMAND = 'flac -dcs %s | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 --add-id3v2 - %s'

__author__ = 'bruno thomas'


class Flac2Mp3(object):
    def lit_meta_flac(self, tags):
        return dict((line.split('=')[0].upper(), line.split('=')[1].replace('\r','\r\n')) for line in tags.replace('\r\n','\r').split('\n'))

    def transcode(self, flac_file, mp3_file):
        tags=self.lit_meta_flac(commands.getoutput('metaflac  --export-tags-to=- %s' % flac_file))

        call(LAME_COMMAND % (flac_file, mp3_file),shell=True)
        tag = eyeD3.Tag(mp3_file)
        tag.link(mp3_file)
        tag.setArtist(tags['ARTIST'])
        tag.setTrackNum([tags['TRACKNUMBER'],tags['TRACKTOTAL']])
        tag.setAlbum(tags['ALBUM'])
        tag.setTitle(tags['TITLE'])
        tag.setGenre(tags['GENRE'])
        tag.setDate(tags['DATE'])
        tag.addImage(ImageFrame.FRONT_COVER, dirname(flac_file) + "/cover.jpg")
        tag.update()

    def trouve_fichiers(self, extension, *repertoires_racines):
        for repertoire_racine in repertoires_racines:
            for root, _, files in os.walk(repertoire_racine):
                for file in files:
                    if file.endswith(extension): yield join(root, file)

    def get_mp3_file(self, mp3_target_path, flac_root_path, flac_file):
        flac_path_relative_to_root = flac_file.replace(flac_root_path, '').replace('.flac', '.mp3')
        if flac_path_relative_to_root.startswith('/'): flac_path_relative_to_root = flac_path_relative_to_root[1:]
        return join(mp3_target_path, flac_path_relative_to_root)

    def run(self, mp3_target_path, flac_root_path, *flac_path_list):
        for flac_file in set(self.trouve_fichiers('.flac', *flac_path_list)):
            target_mp3_file = self.get_mp3_file(mp3_target_path, flac_root_path, flac_file)
            if not isdir(dirname(target_mp3_file)):
                os.makedirs(dirname(target_mp3_file))
            self.transcode(flac_file, target_mp3_file)

class TestFlac2Mp3(unittest.TestCase):
    def test_lit_metaflac_une_ligne(self):
        self.assertEquals({"TITRE" : "titre"}, Flac2Mp3().lit_meta_flac("TITRE=titre"))

    def test_lit_meta_flac_deux_lignes(self):
        self.assertEquals({"TITRE" : "titre", "ALBUM" : "album"}, Flac2Mp3().lit_meta_flac("TITRE=titre\nALBUM=album"))

    def test_lit_meta_flac_deux_lignes_avec_majuscule_minuscule(self):
        self.assertEquals({"TITRE" : "titre", "ALBUM" : "album"}, Flac2Mp3().lit_meta_flac("TiTrE=titre\nalbum=album"))

    def test_lit_meta_flac_deux_lignes_avec_retour_chariot(self):
        self.assertEquals({"DESCRIPTION" : u"Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino", "TITRE" : "titre"},
            Flac2Mp3().lit_meta_flac(u"DESCRIPTION=Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino\nTITRE=titre"))

    def test_get_mp3_dir(self):
        self.assertEquals('/target/dir/song.mp3', Flac2Mp3().get_mp3_file('/target', '/absolute/flac/path/', '/absolute/flac/path/dir/song.flac'))
        self.assertEquals('/target/dir/song.mp3', Flac2Mp3().get_mp3_file('/target', '/absolute/flac/path', '/absolute/flac/path/dir/song.flac'))

    def test_flac2mp3_fichier_ne_terminant_pas_par_flac(self):
        with self.assertRaises(Exception):
            Flac2Mp3().transcode("fichier.blah", "inutile")

    def test_flac2mp3_fichier_inexistant(self):
        with self.assertRaises(Exception):
            Flac2Mp3().transcode("fichier_inexistant.flac", "inutile")