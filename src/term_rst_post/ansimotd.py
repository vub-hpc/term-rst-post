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
Formatting and management of MOTD text files with ANSI escape codes.

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import logging
import os
import re

from textwrap import indent, wrap

from term_rst_post.exit import error_exit

logger = logging.getLogger()


def accomodate_motd(motd_dir, body_file, head_file=None, foot_file=None, wrap_width=70):
    """
    Transform MOTD text file by: wrapping, indenting and adding header/footer
    - motd_dir: (string) path to dir with MOTD messages
    - body_file: (file) text file with MOTD body, it will be updated
    - head_file: (file) text file that will be prepended to body
    - foot_file: (file) text file that will be appended to body
    - wrap_width: (int) max column width of the text file
    """
    motd_text = ''
    motd_parts = [part for part in [head_file, body_file, foot_file] if part]
    logger.debug("Parts included in the MOTD: {}".format(', '.join([part.name for part in motd_parts])))

    # Prepend/Append sections to MOTD
    for part in motd_parts:
        try:
            part_text = part.read()
        except IOError as err:
            error_exit(f"Failed to read text file: '{part.name}'", err)
        else:
            motd_text += part_text
            logger.info(f"Added contents of '{part.name}' to MOTD text file")

    # Format MOTD text file
    try:
        with open(body_file.name, 'w') as motd_file:
            motd_lines = motd_text.splitlines()
            # Wrap text to 70 characters respecting spacings and ANSI escape codes
            for n, line in enumerate(motd_lines):
                motd_lines[n : n + 1] = wrap_ansicode(line, wrap_width, 5)
            # Indent with two spaces
            motd_lines = [indent(l, '  ') for l in motd_lines]
            motd_file.write('\n'.join(motd_lines) + '\n')
    except IOError as err:
        error_exit(f"Failed to open ANSI text file to update its contents: '{body_file.name}'", err)
    else:
        logger.info(f"Reformatted contents of ANSI text file '{body_file.name}' to {wrap_width} characters")
        motd_file.close()

    return motd_file


def enable_motd(motd_cfg, motd_file):
    """
    Enable MOTD message
    - motd_cfg: (string) path to config file in MOTD directory
    - motd_file: (string) path to MOTD message
    """
    motd_filename = os.path.basename(motd_file)

    try:
        with open(motd_cfg, 'w') as cfgfile:
            cfgfile.write(f'{motd_filename}')
    except IOError as err:
        error_exit("Failed to write MOTD configuration file: '{}'".format(motd_cfg), err)
    else:
        logger.debug("Modified MOTD configuration file: '{}'".format(motd_cfg))
        cfgfile.close()


def wrap_ansicode(ansistr, column_width, match_width):
    """
    Cuts long string to column width accounting for ANSI escape code
    - ansistr: (str) text with ANSI escape codes
    - column_width: (int) charcater length of column
    - match_width: (int) number of charcaters to match between text representation
    """
    # Text without ANSI escape codes
    clearstr = re.sub('\033\[[0-9;]*m', '', ansistr)

    if len(clearstr) > column_width + 2:
        # Wrap clear string
        clearstr_wrapped = wrap(
            clearstr, width=column_width, replace_whitespace=False, drop_whitespace=False, break_long_words=False
        )

        # number of ANSI escape codes in the text
        ansicodes = len(ansistr) - len(clearstr)
        logger.debug("Wrapping {} characters long line with {} ANSI escape characters".format(len(clearstr), ansicodes))

        # Replicate wrapped lines of clear text with ansi string
        ansistr_wrapped = list()
        for line in clearstr_wrapped:
            # Define range around column width to look for end of line of clearstr in ansistr
            # 3x match_width to the left and ansicodes to the right
            cutleft = column_width - (match_width * 3)
            cutright = column_width + ansicodes
            match_zone = ansistr[cutleft:cutright]
            # Find the first matching substring
            cutpoint = match_zone.find(line[(match_width * -1) :])
            cutpoint = cutleft + match_width + cutpoint
            # Split ansistr in the same point as clearstr
            leftstr = ansistr[:cutpoint].lstrip()
            ansistr_wrapped.append(leftstr)  # save left part
            ansistr = ansistr[cutpoint:]  # update ansi text with right part
            ansicodes -= len(ansistr_wrapped[-1]) - len(line)  # update number of ANSI codes

        logger.debug(
            "Wrapped long line into {} lines (target is {} lines)".format(len(ansistr_wrapped), len(clearstr_wrapped))
        )
    else:
        ansistr_wrapped = [ansistr]

    return ansistr_wrapped
