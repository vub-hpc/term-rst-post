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


def change_file_extension(filepath, extension, full_path=False):
    """
    Return file name changing its extension
    - filepath: (string) realative or absolute path
    - extension: (string) new extension of file
    - full_path: (boolean) return full path (True) or file name (False)
    """
    new_filepath = Path(filepath).with_suffix(extension)

    if not full_path:
        new_filepath = new_filepath.name

    logger.debug(f"File path '{new_filepath}' with extension '{extension}' generated from path '{filepath}'")

    return new_filepath


def direct_path(rel_path):
    """
    Return path without special maps
    - rel_path: (string) realative path
    """
    special_maps = ['..', '.', '/']

    rel_path = Path(rel_path)
    direct_path_parts = [part for part in rel_path.parts if part not in special_maps]
    direct_path = Path(*direct_path_parts)

    logger.debug(f"Path '{rel_path}' converted to '{direct_path}'")

    return f"{direct_path}"


def resolve_path(filepath):
    """
    Return string with absolute path from filepath
    - filepath: (string) realative or absolute path
    """
    abs_filepath = Path(filepath).resolve()

    logger.debug(f"File path '{filepath}' resolved to '{abs_filepath}'")

    return f"{abs_filepath}"


def common_path_join(left_path, right_path):
    """
    Return path resulting from joining the left and right parts of provided paths
    at common directory. This directory will be the lowest one in the path.
    - left_path: (string) realative or absolute path
    - right_path: (string) realative or absolute path
    """
    left_path = Path(left_path)
    left_parts = left_path.parts

    right_path = Path(right_path)
    right_parts = right_path.parts
    if right_path.is_absolute:
        right_parts = right_parts[1:]  # remove leading slash

    common_dirs = set(left_parts).intersection(right_parts)

    if len(common_dirs) == 0:
        path_list = [f"'{path}'" for path in [left_path, right_path]]
        raise ValueError("Cannot join paths, common directory not found: {}".format(', '.join(path_list)))
    else:
        common_dirs_depth = {comdir: left_parts.index(comdir) for comdir in common_dirs}
        junction_dir = sorted(common_dirs_depth, key=common_dirs_depth.get, reverse=True)[0]

    # Join paths at the junction directory
    try:
        left_depth = left_parts.index(junction_dir)
        right_depth = right_parts.index(junction_dir)
    except ValueError:
        raise ValueError(f"Cannot join paths, junction directory '{junction_dir}' not found")
    else:
        joined_path = Path(*left_parts[:left_depth], *right_parts[right_depth:])
        logger.debug(f"Paths joined at common directory '{junction_dir}': '{joined_path}'")

    return f"{joined_path}"


def rst_path_from_html_link(html_link, html_file):
    """
    Find path to RST file from the link to the corresponding HTML document
    - html_link: (string) link from HTML document
    - html_file: (string) path to HTML file
    """
    # Remove special maps from HTML link
    html_link = Path(direct_path(html_link))
    # Absolute path to HTML file
    html_file = Path(html_file).resolve()

    # Determine path to root directory holding the RST posts
    try:
        # HTML pages are located under '_website'
        root_level = html_file.parts.index('_website')
    except ValueError:
        raise FileNotFoundError("Missing '_website' directory, cannot find RST file from HTML link")
    else:
        rst_root = Path(*html_file.parts[:root_level])

    # Tentative local paths to RST file following HTML link directory structure
    rst_path = rst_root.joinpath(html_link)
    rst_targets = (rst_path, rst_path.with_suffix('.rst'))
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
