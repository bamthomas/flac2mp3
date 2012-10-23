#!/usr/bin/env python
"""
To use this script you'll need flac and lame
Usage :
flac2mp3 [origin directories] mp3/repository/destination
"""
import getopt
from itertools import repeat
from logging import INFO
import logging
from multiprocessing import Pool
import multiprocessing
from posix import getcwd
from struct import unpack
import sys
from genericpath import isdir
import os
from os.path import dirname, join
from subprocess import Popen, PIPE

__author__ = 'bruno thomas'

logging.basicConfig(format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
LOGGER = logging.getLogger('flac2mp3')

LAME_COMMAND = 'lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 --add-id3v2 - %s'
FLAC_COMMAND = 'flac -dcs %s'
VOBIS_COMMENT = 4

def get_cpu_count():
    try:
        return multiprocessing.cpu_count()
    except NotImplementedError:
        return 1

def transcode(flac_file, mp3_file):
    tags = get_flac_tags(get_vobis_comment_bloc(flac_file))
    LOGGER.info('transcoding %s with tags (title=%s artist=%s track=%s/%s)', flac_file, tags['TITLE'], tags['ARTIST'], tags['TRACKNUMBER'], tags['TRACKTOTAL'])

    mp3_tags = list()
    if 'ARTIST' in tags: mp3_tags += ['--ta', tags['ARTIST']]
    if 'ALBUM' in tags: mp3_tags += ['--tl', tags['ALBUM']]
    if 'TITLE' in tags: mp3_tags += ['--tt', tags['TITLE']]
    if 'DESCRIPTION' in tags: mp3_tags += ['--tc', tags['DESCRIPTION']]
    if 'TRACKNUMBER' in tags:
        if 'TRACKTOTAL' in tags:
            mp3_tags += ['--tn', '%s/%s' % (tags['TRACKNUMBER'], tags['TRACKTOTAL'])]
        else:
            mp3_tags += ['--tn', tags['TRACKNUMBER']]

    if 'GENRE' in tags: mp3_tags += ['--tg', tags['GENRE']]
    if 'DATE' in tags: mp3_tags += ['--ty', tags['DATE']]

    cover_file = join(dirname(flac_file), "cover.jpg")
    if os.path.isfile(cover_file): mp3_tags += ['--ti', cover_file]

    flac_command = Popen((FLAC_COMMAND % flac_file).split(' '), stdout=PIPE)
    lame_command=Popen((LAME_COMMAND % mp3_file).split(' '), stdin=flac_command.stdout)
    lame_command.wait()


class MetaflacNotFound(Exception):pass

def get_vobis_comment_bloc(flac_file):
    block = None
    with open(flac_file, 'rb') as flac:
        assert 'fLaC' == flac.read(4)

        last_block = False
        block_type = 0

        while not last_block and block_type is not VOBIS_COMMENT:
            last_block_and_block_type = flac.read(1)
            block_type = ord(last_block_and_block_type) & 0x07
            last_block = ord(last_block_and_block_type) & 0x80 is 0x80
            block_length, = unpack('>i', '\x00' + flac.read(3))
            block = flac.read(int(block_length))
        if block_type is not VOBIS_COMMENT: raise MetaflacNotFound()
    return block

class tags(dict):
    def __init__(self, seq=None, **kwargs):
        super(tags, self).__init__(seq, **kwargs)
    def __missing__(self, _):return None

def get_flac_tags(vobis_comment_block):
    vendor_length, = unpack('I', vobis_comment_block[0:4])
    offset = 4 + vendor_length
    user_comment_list_length, = unpack('I', vobis_comment_block[offset:offset + 4])
    offset += 4
    comments = list()
    for vobis_comment_index in range(user_comment_list_length):
        length, = unpack('I', vobis_comment_block[offset:offset + 4])
        offset += 4
        comments.append(vobis_comment_block[offset:offset + length])
        offset += length
    return tags(split_key_value_at_first_equal_and_upper_key(comment) for comment in comments)

def find_files(extension, *root_dirs):
    for root_dir in root_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(extension): yield join(root, file)

def get_mp3_filename(mp3_target_path, flac_root_path, flac_file):
    flac_path_relative_to_root = flac_file.replace(flac_root_path, '').replace('.flac', '.mp3')
    if flac_path_relative_to_root.startswith('/'): flac_path_relative_to_root = flac_path_relative_to_root[1:]
    return join(mp3_target_path, flac_path_relative_to_root)

def process_transcoding((flac_file, flac_root_path, mp3_target_path)):
    try:
        target_mp3_file = get_mp3_filename(mp3_target_path, flac_root_path, flac_file)
        if not isdir(dirname(target_mp3_file)):
            try:
                os.makedirs(dirname(target_mp3_file))
            except OSError:
                pass # other thread might have been faster
        transcode(flac_file, target_mp3_file)
    except Exception as e:
        LOGGER.error('error during the transcoding of %s : %s' % (flac_file, e))

def which(program):
    def is_exe(fpath): return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

def run(mp3_target_path, flac_root_path, *flac_path_list):
    flac_files = set(find_files('.flac', *flac_path_list))
    cpu_count = get_cpu_count()
    LOGGER.info('found %d cpu(s)', cpu_count)
    LOGGER.info('found %d flac files', len(flac_files))
    LOGGER.info('transcoding files with command "%s" | %s', FLAC_COMMAND % 'file.flac',LAME_COMMAND  % 'file.mp3')

    Pool(cpu_count).map(process_transcoding, zip(flac_files, repeat(flac_root_path), repeat(mp3_target_path)))

def split_key_value_at_first_equal_and_upper_key(string_with_equal):
    k,v = string_with_equal.split('=', 1)
    return k.upper(), v

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

        if not which('lame'):
            LOGGER.fatal("Cannot find lame. Please install lame: http://lame.sourceforge.net/")
            return 3
        if not which('flac'):
            LOGGER.fatal("Cannot find flac. Please install flac: http://flac.sourceforge.net/")
            return 3

        run(mp3_target_path, getcwd(), *args)
    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    LOGGER.setLevel(INFO)
    sys.exit(main(sys.argv))
