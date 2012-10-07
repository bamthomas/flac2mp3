# -*- coding: UTF-8 -*-
import commands
from os.path import dirname
from subprocess import call
import unittest
import eyeD3
from eyeD3.frames import ImageFrame

LAME_COMMAND = 'flac -dcs %s | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 --add-id3v2 - %s'

__author__ = 'bruno thomas'

class Flac2Mp3(object):
    def lit_meta_flac(self, tags):
        return dict((line.split('=')[0].upper(), line.split('=')[1].replace('\r','\r\n')) for line in tags.replace('\r\n','\r').split('\n'))

    def run(self, flac_file, export_path):
        tags=self.lit_meta_flac(commands.getoutput('metaflac  --export-tags-to=- %s' % flac_file))
        mp3_file = flac_file.replace('.flac', '.mp3')
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