# -*- coding: UTF-8 -*-
import unittest
from flac2mp3 import lit_meta_flac, get_mp3_file, transcode

__author__ = 'bruno thomas'

class TestFlac2Mp3(unittest.TestCase):
    def test_lit_metaflac_une_ligne(self):
        self.assertEquals({"TITRE" : "titre"}, lit_meta_flac("TITRE=titre"))

    def test_lit_meta_flac_deux_lignes(self):
        self.assertEquals({"TITRE" : "titre", "ALBUM" : "album"}, lit_meta_flac("TITRE=titre\nALBUM=album"))

    def test_lit_meta_flac_deux_lignes_avec_majuscule_minuscule(self):
        self.assertEquals({"TITRE" : "titre", "ALBUM" : "album"}, lit_meta_flac("TiTrE=titre\nalbum=album"))

    def test_lit_meta_flac_deux_lignes_avec_retour_chariot(self):
        self.assertEquals({"DESCRIPTION" : u"Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino", "TITRE" : "titre"},
            lit_meta_flac(u"DESCRIPTION=Interprètes : Hot Chip, interprète\r\nLabel : Domino Recording Co - Domino\nTITRE=titre"))

    def test_get_mp3_dir(self):
        self.assertEquals('/target/dir/song.mp3', get_mp3_file('/target', '/absolute/flac/path/', '/absolute/flac/path/dir/song.flac'))
        self.assertEquals('/target/dir/song.mp3', get_mp3_file('/target', '/absolute/flac/path', '/absolute/flac/path/dir/song.flac'))

    def test_flac2mp3_fichier_ne_terminant_pas_par_flac(self):
        with self.assertRaises(Exception):
            transcode("fichier.blah", "inutile")

    def test_flac2mp3_fichier_inexistant(self):
        with self.assertRaises(Exception):
            transcode("fichier_inexistant.flac", "inutile")