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


def bottom_dir(filepath):
    """
    Return string with name of last dir in the path
    Only uses path heuristics, avoiding checking the filesystem with is_file() or is_dir()
    - filepath: (string) realative or absolute path
    """
    # pathlib ignores trailing slashes, use os.path
    dirpath = os.path.dirname(filepath)
    lastdir = os.path.basename(dirpath)

    logger.debug(f"Last directory in '{filepath}' determined as '{lastdir}'")

    return f"{lastdir}"


def rst_path_from_html_link(html_link, html_file):
    """
    Find path to RST file from the link to the corresponding HTML document
    - html_link: (string) link from HTML document
    - html_file: (string) path to HTML file
    """
    # Remove special maps from HTML link
    html_link_parts = [part for part in Path(html_link).parts if part not in ['..', '.', '/']]
    html_link = Path(*html_link_parts)
    # Absolute path to HTML file
    html_file = Path(html_file).resolve()

    # Determine path to root directory holding the RST posts
    try:
        # HTML pages are located under '_website'
        root_level = html_file.parts.index('_website')
    except ValueError:
        raise FileNotFoundError(f"Missing '_website' directory, cannot find RST file from HTML link")
    else:
        rst_root = Path(*html_file.parts[:root_level])

    # Tentative local paths to RST file following HTML link directory structure
    rst_path = rst_root.joinpath(html_link)
    rst_targets = (rst_path, rst_path.with_suffix('.rst'))
    print(rst_targets)
    logger.debug("Tentative paths to RST files: {}".format(','.join([f"'{path}'" for path in rst_targets])))

    rst_file = None

    for target in rst_targets:
        try:
            rst_file = target.resolve(strict=True)
        except FileNotFoundError:
            logger.debug(f"Tentative RST file not found: '{target}'")

    if rst_file and rst_file.is_file():
        logger.debug(f"Found RST file: '{rst_file}'")
        return f"{rst_file}"
    else:
        raise FileNotFoundError(f"Could not find RST file '{html_link.name}' in '{rst_root}'")
