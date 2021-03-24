#
# Copyright 2021-2021 Vrije Universiteit Brussel
#
# This file is part of term_rst_post,
# originally created by the HPC team of Vrije Universiteit Brussel (https://hpc.vub.be),
# with support of Vrije Universiteit Brussel (https://www.vub.be),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/sisc-hpc/term_rst_post
#
# term_rst_post is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v3.
#
# term_rst_post is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this code.  If not, see <http://www.gnu.org/licenses/>.
#
##
"""
File handling tools for term_rst_post

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import argparse
import logging
import os

from pathlib import Path

logger = logging.getLogger()


def valid_dirpath(dirpath):
    """
    Validate directory path passed through argparse
    - dirpath: (string) path
    """
    if os.path.isdir(dirpath):
        return dirpath
    else:
        errmsg = f"Directory '{dirpath}' does not exist"
        raise argparse.ArgumentTypeError(errmsg)


def fileobj_extension(fileobj):
    """
    Return extension (if any) of file object
    - fileobj: file object
    """
    filepath = Path(fileobj.name)

    return filepath.suffix


def change_file_extension(filepath, extension):
    """
    Return file name changing its extension
    - filepath: (string) realative or absolute path
    - extension: (string) new extension of file
    """
    new_filepath = Path(filepath).with_suffix(extension)

    logger.debug(f"File name '{new_filepath.name}' with extension '{extension}' generated from path '{filepath}'")

    return new_filepath.name


def resolve_path(filepath):
    """
    Return string with absolute path from filepath
    - filepath: (string) realative or absolute path
    """
    abs_filepath = Path(filepath).resolve()

    logger.debug(f"File path '{filepath}' resolved to '{abs_filepath}'")

    return f"{abs_filepath}"


def rst_path_from_html_link(link_path, root_path):
    """
    Generate absolute path from relative link
    - link_path: (string) relative link from HTML document
    - root_dir: (string) path to root directory of news posts in RST format
    """
    html_link = Path(link_path)
    rst_root = Path(root_path)

    # Make tentative paths to RST file in provided root directory
    root_level = html_link.parts.index(rst_root.name) + 1
    rst_path = Path(root_path, *html_link.parts[root_level:])
    rst_targets = (rst_path, rst_path.with_suffix('.rst'))

    rst_file = None

    for target in rst_targets:
        try:
            rst_file = target.resolve(strict=True)
        except FileNotFoundError:
            logger.debug("Tentative RST file not found: '{}'".format(target))

    if rst_file and rst_file.is_file():
        logger.debug("Found RST file: '{}'".format(rst_file))
        return f"{rst_file}"
    else:
        raise FileNotFoundError(f"Could not find RST file '{html_link.name}' in '{rst_root}'")
