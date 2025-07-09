"""
Helper to use pyzipper from CLI

Designed to help with manual testing and double-check the result using 7zip

Create an archive using 7zip:
* 7za a -tzip -pPASSWORD -mem=AES256 -mm=STORE result_file.zip source_dir_or_file
* 7za a -tzip -pPASSWORD -mem=AES256 -mm=DEFLATE result_file.zip source_dir_or_file
* 7za a -tzip -ptpPASSWORDst -mem=AES256 -mm=LZMA result_file.zip source_dir_or_file

Extract using 7zip:
* 7za x -pPASSWORD source_file.zip

"""
import argparse
import sys
import pathlib
import os


from pyzipper import zipfile
from pyzipper import zipfile_aes


parser = argparse.ArgumentParser(
    prog='pyzipper',
    description='Zip files with AES encryption.',
    epilog='')
parser.add_argument('filename')
parser.add_argument(
    '-x', '--extract', action='store_true', help='Extract all files with full path.')
parser.add_argument(
    '-c', '--create', action='store_true', help='Create a new archive.')
parser.add_argument(
    '-l', '--list', action='store_true', help='List archive members.')
parser.add_argument('-t', '--target', default='.', help='Base path where to extract or add files.')
parser.add_argument('-p', '--password')
parser.add_argument(
    '--lzma', action='store_true', default=False, help='Compress using LZMA, otherwise use DEFLATE')
parser.add_argument(
    '--stored', action='store_true', default=False, help='Disable compression.')
parser.add_argument(
    '-v', '--verbose', action='store_true', default=False)
parser.add_argument(
    '--aes-256', action='store_true', default=False, help='Encrypt with 256 bites. Default is 128 bits.')


def zip_list(args):
    """
    List the content of the archive.
    """
    with zipfile_aes.AESZipFile(args.filename) as archive:
        for name in archive.namelist():
            print(name)
    return 0


def zip_extract(args):
    """
    Extract all members of the archive with full path.
    """
    with zipfile_aes.AESZipFile(args.filename) as archive:
        archive.setpassword(args.password.encode('utf-8'))
        base = pathlib.Path(args.target).absolute()
        if not base.exists():
            base.mkdir()
        os.chdir(base)

        for name in archive.namelist():
            result = archive.extract(name)
            if args.verbose:
                print(result)
        return 0


def zip_create(args):
    """
    Extract all members of the archive with full path.
    """
    compression = zipfile.ZIP_DEFLATED
    if args.lzma:
        compression = zipfile.ZIP_LZMA
    if args.stored:
        compression = zipfile.ZIP_STORED

    key_size = 128
    if args.aes_256:
        key_size = 256

    base = pathlib.Path(args.target)

    with zipfile_aes.AESZipFile(
        args.filename,
        mode='w',
        compression=compression,
            ) as archive:
        archive.setpassword(args.password.encode('utf-8'))
        archive.setencryption(zipfile_aes.WZ_AES, nbits=key_size)
        archive.write(base)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.list:
        sys.exit(zip_list(args))

    if args.extract:
        sys.exit(zip_extract(args))

    if args.create:
        sys.exit(zip_create(args))

    parser.print_help()
    sys.exit(1)
