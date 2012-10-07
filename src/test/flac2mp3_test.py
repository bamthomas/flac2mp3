# -*- coding: UTF-8 -*-
import commands
import unittest

__author__ = 'bruno thomas'

class Flac2Mp3(object):
    def lit_meta_flac(self, tags):
        return dict((line.split('=')[0].upper(), line.split('=')[1].replace('\r','\r\n')) for line in tags.replace('\r\n','\r').split('\n'))
    
    def run(self, flac_file, export_path):
        tags=self.lit_meta_flac(commands.getoutput('metaflac  --export-tags-to=- %s' % flac_file))

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

    def test_flac2mp3_fichier_ne_terminant_pas_par_flac(self):
        with self.assertRaises(Exception):
            Flac2Mp3().run("fichier.blah", "inutile")

    def test_flac2mp3_fichier_inexistant(self):
        with self.assertRaises(Exception):
            Flac2Mp3().run("fichier_inexistant.flac", "inutile")