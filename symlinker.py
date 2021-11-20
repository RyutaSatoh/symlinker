import argparse
import logging
import os

from filecmp import dircmp
from typing import List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', '-s', required=True)
    parser.add_argument('--dst', '-d', required=True)
    parser.add_argument('--filter_ext', '-f', nargs='*', default=['mov', 'm4a', 'mp4', '3gp'])

    return parser.parse_args()


def check_srconly_and_symlink(src: str, dst: str, dc: dircmp, filter_ext: List[str]) -> None:
    srconly = dc.left_only

    for p in srconly:
        if p.startswith('.'):
            # a file or dir starts with . should be ignored
            continue

        splitext = os.path.splitext(p)

        if splitext[1] != '':
            # TODO
            # Currently directories must be named without extension.
            # This is OK for my environment, but not a general prerequirement.
            # os.path.isdir should be checked first.

            if len(splitext[1]) > 2 and splitext[1][1:].lower() not in filter_ext:
                # only if a path ...
                # * has an extension
                # * an extension not in filter list

                src_path = os.path.join(src, p)
                dst_path = os.path.join(dst, p)
                src_rel_path = os.path.relpath(src_path, dst)
                os.symlink(
                    src_rel_path,
                    dst_path
                )

        else:
            # no extensions, probably a directory
            new_src_dir = os.path.join(src, p)
            if os.path.isdir(new_src_dir):
                # it is directory, mkdir it and go into it
                new_dst_dir = os.path.join(dst, p)
                os.mkdir(new_dst_dir)

                # For simplicity, use same code even when
                # clearly comparison is not needed
                subdc = dircmp(new_src_dir, new_dst_dir)
                check_srconly_and_symlink(
                    new_src_dir,
                    new_dst_dir,
                    subdc,
                    filter_ext
                )

    # check sub directories
    for subdc in dc.subdirs.values():
        check_srconly_and_symlink(
            os.path.join(src, subdc.left),
            os.path.join(dst, subdc.right),
            subdc,
            filter_ext
        )


def main() -> None:
    args = parse_args()

    if not os.path.exists(args.src):
        logging.error(f'source path not found ({args.src})')
        exit(-1)
    if not os.path.isdir(args.src):
        logging.error(f'source path is not a directory ({args.src})')
        exit(-1)

    if not os.path.exists(args.dst):
        logging.error(f'destination path not found ({args.dst})')
        exit(-1)
    if not os.path.isdir(args.dst):
        logging.error(f'destination path is not a directory ({args.dst})')
        exit(-1)

    dc = dircmp(args.src, args.dst)
    check_srconly_and_symlink(
        args.src, args.dst, dc, args.filter_ext
    )


if __name__ == '__main__':
    main()
