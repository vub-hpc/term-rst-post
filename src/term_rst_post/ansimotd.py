#
# Copyright 2021-2021 Vrije Universiteit Brussel
#
# This file is part of term-rst-post,
# originally created by the HPC team of Vrije Universiteit Brussel (https://hpc.vub.be),
# with support of Vrije Universiteit Brussel (https://www.vub.be),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/vub-hpc/term-rst-post
#
# term-rst-post is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v3.
#
# term-rst-post is distributed in the hope that it will be useful,
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
import re

from textwrap import wrap

from term_rst_post.exit import error_exit

logger = logging.getLogger()


def accomodate_motd(body_file, head_file=None, foot_file=None, foot_link=None, wrap_width=80):
    """
    Transform MOTD text file by: adding header/footer and wrapping to a fixed width
    - body_file: (file) text file with MOTD body, it will be updated
    - head_file: (file) text file that will be prepended to body
    - foot_file: (file) text file that will be appended to body
    - foot_link: (string) URL for an extra link after the body
    - wrap_width: (int) max column width of the text file (disable with 0)
    """
    motd_text = list()

    # Read sections of MOTD
    motd_parts = {
        "head": head_file,
        "body": body_file,
        "foot": foot_file,
    }

    active_parts = [part for part in motd_parts if motd_parts[part]]
    logger.debug("Parts included in the MOTD: {}".format(', '.join([motd_parts[part].name for part in active_parts])))

    for part in active_parts:
        try:
            part_text = motd_parts[part].read()
        except IOError as err:
            error_exit(f"Failed to read text file: '{motd_parts[part].name}'", err)
        else:
            logger.info(f"Adding contents of '{motd_parts[part].name}' to ANSI text file")
            motd_parts[part] = part_text

    # Soft unwrap body of MOTD keeping double new-lines (i.e. paragraphs)
    body_unwrapped = re.sub("(.)\n(?!\n)", r"\1 ", motd_parts["body"])
    motd_parts["body"] = body_unwrapped + "\n"

    # Inject extra link between body and footer
    if foot_link:
        foot_text = motd_parts["foot"]
        if foot_text is None:
            foot_text = ""

        foot_link_text = f"\nMore information in\n{foot_link}\n"
        motd_parts["foot"] = foot_link_text + foot_text

    # Check for long URLs
    if wrap_width > 0:
        http_urls = re.findall(r'(https?://[^\s]+)', motd_parts["body"])
        for url in http_urls:
            if len(url) > wrap_width:
                logger.warning(f"Found a URL longer than ANSI text width: {url} ({len(url)} char)")

    # Format MOTD text file
    motd_text = ''.join([motd_parts[part] for part in motd_parts if motd_parts[part]])

    try:
        with open(body_file.name, 'w') as motd_file:
            motd_lines = motd_text.splitlines()
            # Wrap text to default column width respecting spacings and ANSI escape codes
            for n, line in enumerate(motd_lines):
                motd_lines[n : n + 1] = wrap_ansicode(line, wrap_width)
            motd_file.write('\n'.join(motd_lines) + '\n')
    except IOError as err:
        error_exit(f"Failed to open ANSI text file to update its contents: '{body_file.name}'", err)
    else:
        logger.info(f"Saved formatted contents of ANSI text file to '{body_file.name}'")
        motd_file.close()

    return motd_file


def wrap_ansicode(ansistr, column_width, match_width=5):
    """
    Cuts long text in a single string to a fixed column width accounting for ANSI escape code characters
    - ansistr: (str) text with ANSI escape codes
    - column_width: (int) length of text column in legible characters
    - match_width: (int) number of characters used to match between the text with/without ANSI escape codes
    """
    # Clear text without the ANSI escape codes
    clearstr = re.sub('\033\[[0-9;]*m', '', ansistr)

    if column_width > 0 and len(clearstr) > column_width:
        # Wrap non-ANSI string
        clearstr_wrapped = wrap(
            clearstr, width=column_width, replace_whitespace=False, drop_whitespace=False, break_long_words=False
        )

        # number of ANSI escape codes in the text
        ansicodes = len(ansistr) - len(clearstr)
        logger.debug(f"Wrapping {len(clearstr)} characters long line with {ansicodes} ANSI escape characters")

        # Replicate wrapped lines of clear text with ansi string
        ansistr_wrapped = list()
        for line in clearstr_wrapped:
            # Define search zone in ANSI text around column width boundary of non-ANSI text to find a match between them
            # search zone = 3x `match_width` to the left and `ansicodes` to the right
            cutleft = column_width - (match_width * 3)
            cutright = column_width + ansicodes
            match_zone = ansistr[cutleft:cutright]
            # Find first matching substring between end of non-ANSI line and ANSI text
            match_start = match_zone.find(line[(match_width * -1) :])
            if match_start < 0:
                # Hard wrap without a match (probably just an empty line)
                cutpoint = column_width
                log_msg = f"Hard wrap at {cutpoint} characters. No match found: '{line}' in '{match_zone}'"
                logger.warning(log_msg) if match_zone else logger.debug(log_msg)
            else:
                cutpoint = cutleft + match_start + match_width
            # Split ANSI text in the same text position as non-ANSI text
            leftstr = ansistr[:cutpoint].lstrip()
            ansistr_wrapped.append(leftstr)  # save left part
            ansistr = ansistr[cutpoint:]  # update ANSI text with right part
            ansicodes -= len(ansistr_wrapped[-1]) - len(line)  # update number of ANSI escape code charcaters

        logger.debug(
            f"Wrapped long line into {len(ansistr_wrapped)} lines (target was {len(clearstr_wrapped)} lines)"
        )
    else:
        ansistr_wrapped = [ansistr]

    return ansistr_wrapped
