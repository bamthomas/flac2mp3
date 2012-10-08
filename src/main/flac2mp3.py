#!/usr/bin/env python
"""
usage message.
"""
import commands
import getopt
from logging import INFO
import logging
from multiprocessing import Pool
from posix import getcwd
import sys
from genericpath import isdir
import os
from os.path import dirname, join
from subprocess import call, check_output
import eyeD3
from eyeD3.frames import ImageFrame

__author__ = 'bruno thomas'

LAME_COMMAND = 'flac -dcs %s | lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 --add-id3v2 - %s'
POOL_SIZE = int(check_output('cat /proc/cpuinfo | grep processor | wc -l', shell=True))
logging.basicConfig(format='[%(name)s] %(levelno)s: %(threadName)s) %(message)s' )
LOGGER=logging.getLogger('flac2mp3')

def lit_meta_flac(tags):
    return dict((line.split('=')[0].upper(), line.split('=')[1].replace('\r','\r\n')) for line in tags.replace('\r\n','\r').split('\n'))

def transcode(flac_file, mp3_file):
    tags=lit_meta_flac(commands.getoutput('metaflac  --export-tags-to=- %s' % flac_file))
    LOGGER.info('transcoding %s with tags (title=%s artist=%s)', flac_file, tags['TITLE'], tags['ARTIST'])
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

def trouve_fichiers(extension, *repertoires_racines):
    for repertoire_racine in repertoires_racines:
        for root, _, files in os.walk(repertoire_racine):
            for file in files:
                if file.endswith(extension): yield join(root, file)

def get_mp3_file(mp3_target_path, flac_root_path, flac_file):
    flac_path_relative_to_root = flac_file.replace(flac_root_path, '').replace('.flac', '.mp3')
    if flac_path_relative_to_root.startswith('/'): flac_path_relative_to_root = flac_path_relative_to_root[1:]
    return join(mp3_target_path, flac_path_relative_to_root)

def process_transcoding(flac_file, flac_root_path, mp3_target_path):
        target_mp3_file = get_mp3_file(mp3_target_path, flac_root_path, flac_file)
        if not isdir(dirname(target_mp3_file)):
            os.makedirs(dirname(target_mp3_file))
        transcode(flac_file, target_mp3_file)

def run(mp3_target_path, flac_root_path, *flac_path_list):
    flac_files = set(trouve_fichiers('.flac', *flac_path_list))
    LOGGER.info('found %d flac files', len(flac_files))
    LOGGER.info('transcoding files with command "%s"', LAME_COMMAND % ('file.flac','file.mp3'))

    thread_pool = Pool(POOL_SIZE)

    for flac_file in flac_files:
        thread_pool.apply_async(process_transcoding, args=(flac_file, flac_root_path, mp3_target_path))
    thread_pool.close()
    thread_pool.join()

class Usage(Exception):
    def __init__(self, msg, *args, **kwargs):
        super(Usage, self).__init__(*args, **kwargs)
        self.msg = msg

def main(argv):
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
            if args:
                mp3_target_path = args.pop()
            else:
                mp3_target_path = './'

        except getopt.error, msg:
            raise Usage(msg)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print __doc__
                return 0

        LOGGER.setLevel(INFO)
        LOGGER.info('found %d processing unit', POOL_SIZE)

        run(mp3_target_path, getcwd(), *args)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv))