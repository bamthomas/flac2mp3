import commands
from genericpath import isdir
import os
from os.path import dirname, join
from subprocess import call
import eyeD3
from eyeD3.frames import ImageFrame

__author__ = 'bruno thomas'

LAME_COMMAND = 'flac -dcs %s | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 --add-id3v2 - %s'

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
