#!/usr/bin/env python
"""
To use this script you'll need flac and lame
Usage :
flac2mp3 [origin directories containing flac files] mp3/repository/destination
"""
import getopt
from itertools import repeat
from logging import INFO
import logging
from multiprocessing import Pool
import multiprocessing
import locale
import re
from struct import unpack, unpack_from
import sys
from tempfile import mkstemp
from genericpath import isdir, isfile
import os
from os.path import dirname, join
from subprocess import Popen, PIPE

__author__ = 'bruno thomas'

logging.basicConfig(format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
LOGGER = logging.getLogger('flac2mp3')

LAME_COMMAND = 'lame --silent -V2 --vbr-new -q0 --lowpass 19.7 --resample 44100 --add-id3v2'
FILE_SYSTEM_ENCODING = sys.getfilesystemencoding()
VOBIS_COMMENT = 4
PICTURE = 6

vobis_comments_lame_opts_map = {
    'ARTIST': '--ta',
    'ALBUM': '--tl',
    'TITLE': '--tt',
    'DESCRIPTION': '--tc',
    'GENRE': '--tg',
    'DATE': '--ty',
    'TRACKNUMBER': '--tn',
    'TRACKTOTAL': 'total'
}


class VobisCommentParser(object):
    image = None
    flac_tags = {}

    def parse(self, flac_file):
        with open(flac_file, 'rb') as flac:
            assert b'fLaC' == flac.read(4)

            last_block = False
            block_type = 0

            while not last_block:
                last_block_and_block_type = flac.read(1)
                block_type = ord(last_block_and_block_type) & 0x07
                last_block = ord(last_block_and_block_type) & 0x80 == 0x80
                block_length, = unpack('>i', b'\x00' + flac.read(3))
                block = flac.read(int(block_length))
                if block_type is VOBIS_COMMENT:
                    self.flac_tags = self.get_flac_tags(block)
                if block_type is PICTURE:
                    self.image = self.get_image_data(block)

        if not self.flac_tags:
            raise RuntimeError('cannot find vobis comment vobis_comment_block in %s' % flac_file)
        return self

    def get_image_data(self, image_block):
        offset = 4
        mime_type_length, = unpack_from('>i', image_block, offset)
        offset += 4 + mime_type_length
        description_length, = unpack_from('>i', image_block, offset)
        offset += 20 + description_length
        image_lenth, = unpack_from('>i', image_block, offset)
        offset += 4
        return image_block[offset:offset + image_lenth]

    def get_flac_tags(self, vobis_comment_block):
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
        return dict(split_key_value_at_first_equal_and_upper_key(comment) for comment in comments)


class CoverFile(object):
    cover_file = None
    image_data = None
    tmp_prefix = 'flac2mp3'
    tmp_suffix = '.tmp'

    def __init__(self, flac_file, image_data):
        cover_file = join(dirname(flac_file), "cover.jpg")
        if os.path.isfile(cover_file):
            self.cover_file = cover_file
        elif image_data:
            self.image_data = image_data
            _, self.cover_file = mkstemp(prefix=self.tmp_prefix, suffix=self.tmp_suffix)

    def __enter__(self):
        if self.image_data:
            with open(self.cover_file, 'wb') as cover:
                cover.write(self.image_data)
        return self

    def __exit__(self, type, value, traceback):
        if self.image_data: os.remove(self.cover_file)

    def exist(self):
        return self.cover_file is not None

    def path(self):
        return self.cover_file


def transcode(flac_file, mp3_file):
    parser = VobisCommentParser().parse(flac_file)
    LOGGER.info('transcoding "%s" with tags (title="%s" artist="%s" track=%s/%s)', flac_file,
                parser.flac_tags.get('TITLE'),
                parser.flac_tags.get('ARTIST'), parser.flac_tags.get('TRACKNUMBER'), parser.flac_tags.get('TRACKTOTAL'))

    lame_tags = dict((vobis_comments_lame_opts_map.get(k), v) for k, v in parser.flac_tags.items())
    if 'total' in lame_tags:
        lame_tags['--tn'] = '%s/%s' % (parser.flac_tags['TRACKNUMBER'], lame_tags.pop('total'))

    encoding = locale.getpreferredencoding()
    with CoverFile(flac_file, parser.image) as cover_file:
        if cover_file.exist(): lame_tags['--ti'] = cover_file.path()

        lame_command_list = LAME_COMMAND.split(' ')
        lame_command_list.extend(arg for (k, v) in lame_tags.items() if k for arg in (k, v.encode(encoding)))
        lame_command_list.extend(('-', mp3_file.encode(FILE_SYSTEM_ENCODING)))

        flac_command = Popen(('flac', '--totally-silent', '-dc', flac_file.encode(FILE_SYSTEM_ENCODING)), stdout=PIPE)
        lame_command = Popen(lame_command_list, stdin=flac_command.stdout)
        lame_command.wait()


def find_files(pattern, *root_dirs):
    regexp = re.compile(pattern)
    for root_dir in root_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if regexp.match(file):
                    yield join(root, file)


def get_mp3_filename(mp3_target_path, flac_root_path, flac_file):
    flac_path_relative_to_root = flac_file.replace(flac_root_path, '').replace('.flac', '.mp3')
    if flac_path_relative_to_root.startswith('/'): flac_path_relative_to_root = flac_path_relative_to_root[1:]
    return join(mp3_target_path, flac_path_relative_to_root)


def tags_are_equals(flac_file, target_mp3_file):
    try:
        import eyed3

        mp3_tags = eyed3.load(target_mp3_file).tag
        parser = VobisCommentParser().parse(flac_file)

        return \
            parser.flac_tags.get('ARTIST') == mp3_tags.artist and \
            parser.flac_tags.get('ALBUM') == mp3_tags.album and \
            parser.flac_tags.get('TITLE') == mp3_tags.title and \
            parser.flac_tags.get('GENRE') == mp3_tags.genre.name and \
            parser.flac_tags.get('DATE') == mp3_tags.year and \
            int(parser.flac_tags.get('TRACKNUMBER')) == mp3_tags.track_num[0] and \
            (not parser.flac_tags.get('TRACKTOTAL') or int(parser.flac_tags.get('TRACKTOTAL')) == mp3_tags.track_num[1])
    except ImportError:
        return False


def process_transcoding(params):
    flac_file, flac_root_path, mp3_target_path = params
    try:
        target_mp3_file = get_mp3_filename(mp3_target_path, flac_root_path, flac_file)
        if not isdir(dirname(target_mp3_file)):
            try:
                os.makedirs(dirname(target_mp3_file))
            except OSError:
                pass # other thread might have been faster
        if isfile(target_mp3_file) and tags_are_equals(flac_file, target_mp3_file):
            LOGGER.info('skipping %r as target mp3 file exists and seems to have the same tags', flac_file)
        else:
            transcode(flac_file, target_mp3_file)
    except Exception as e:
        LOGGER.exception('error during the transcoding of %r : %s' % (flac_file, e))


def which(program):
    def is_exe(fpath):
        return isfile(fpath) and os.access(fpath, os.X_OK)

    for path in os.environ["PATH"].split(os.pathsep):
        exe_files = os.path.join(path, program), os.path.join(path, program + '.exe')
        for exe_file in exe_files:
            if is_exe(exe_file):
                return exe_file


def get_cpu_count():
    try:
        return multiprocessing.cpu_count()
    except NotImplementedError:
        return 1


def run(mp3_target_path, flac_root_path, *flac_path_list):
    flac_files = set(find_files('.*\.flac', *flac_path_list))
    cpu_count = get_cpu_count()
    LOGGER.info('found %d cpu(s)', cpu_count)
    LOGGER.info('found %d flac files', len(flac_files))
    LOGGER.info('transcoding files with command "%s"', LAME_COMMAND)

    Pool(cpu_count).map(process_transcoding, zip(flac_files, repeat(flac_root_path), repeat(mp3_target_path)))

    LOGGER.info('transcoding done, exiting normally')


def split_key_value_at_first_equal_and_upper_key(string_with_equal):
    k, v = string_with_equal.split(b'=', 1)
    # vobis comments are utf-8 http://www.xiph.org/vorbis/doc/v-comment.html
    return k.decode('utf-8').upper(), v.decode('utf-8')


class Usage(Exception):
    def __init__(self, msg, *args, **kwargs):
        super(Usage, self).__init__(args, kwargs)
        self.msg = msg


def main():
    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.error as msg:
            raise Usage(msg)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(__doc__)
                return 0

        if args:
            mp3_target_path = args.pop()
        else:
            raise Usage('no mp3 target directory given')

        if not which('lame'):
            LOGGER.fatal("Cannot find lame. Please install lame: http://lame.sourceforge.net/")
            return 3
        if not which('flac'):
            LOGGER.fatal("Cannot find flac. Please install flac: http://flac.sourceforge.net/")
            return 3

        run(mp3_target_path, os.getcwd(), *args)
        return 0
    except Usage as err:
        print("for help use -h or --help", err)
        return 2


if __name__ == "__main__":
    LOGGER.setLevel(INFO)
    sys.exit(main())
