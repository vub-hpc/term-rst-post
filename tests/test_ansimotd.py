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
Unit tests for term_rst_post.ansimotd

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import os
import pytest
import shutil

from term_rst_post import ansimotd


@pytest.fixture
def unwrap_text(exampledir):
    return os.path.join(exampledir, 'ablog_motd_unwrapped.ansi')


@pytest.fixture
def head_text(exampledir):
    return os.path.join(exampledir, 'ablog_motd_head.ansi')


@pytest.fixture
def foot_text(exampledir):
    return os.path.join(exampledir, 'ablog_motd_foot.ansi')


@pytest.fixture
def wrap_text(refdir):
    return os.path.join(refdir, 'ablog_motd_wrapped.ansi')


@pytest.fixture
def wrap_indent_text(refdir):
    return os.path.join(refdir, 'ablog_motd_wrapped_indented.ansi')


@pytest.fixture
def wrap_headfoot_text(refdir):
    return os.path.join(refdir, 'ablog_motd_wrapped_headfoot.ansi')


@pytest.fixture
def wrap_indent_url_text(refdir):
    return os.path.join(refdir, 'ablog_motd_wrapped_indented_url.ansi')


@pytest.fixture
def wrap_headfoot_url_text(refdir):
    return os.path.join(refdir, 'ablog_motd_wrapped_headfoot_url.ansi')


@pytest.fixture
def test_url():
    return 'https://example.com/posts/year/test'


def test_wrap_ansicode(unwrap_text, wrap_text):

    with open(unwrap_text, 'r') as testfile:
        # Wrap text to 70 characters column width
        test_lines = testfile.read().splitlines()
        for n, line in enumerate(test_lines):
            test_lines[n : n + 1] = ansimotd.wrap_ansicode(line, 70, 5)
        test_motd = '\n'.join(test_lines) + '\n'

    with open(wrap_text, 'r') as reffile:
        reference_motd = reffile.read()

    assert test_motd == reference_motd


def test_accomodate_motd(tmpdir, unwrap_text, wrap_indent_text):
    # Copy input text to tmpdir to avoid updating file in example dir
    test_filepath = os.path.join(tmpdir, os.path.basename(unwrap_text))
    shutil.copy(unwrap_text, test_filepath)

    with open(test_filepath, 'r') as testfile:
        ansimotd.accomodate_motd(testfile)
        testfile.seek(0)
        test_motd = testfile.read()

    with open(wrap_indent_text, 'r') as reffile:
        reference_motd = reffile.read()

    assert test_motd == reference_motd


def test_accomodate_motd_head_foot(tmpdir, unwrap_text, head_text, foot_text, wrap_headfoot_text):
    # Copy input text to tmpdir to avoid updating file in example dir
    test_filepath = os.path.join(tmpdir, os.path.basename(unwrap_text))
    shutil.copy(unwrap_text, test_filepath)

    with open(test_filepath, 'r') as testfile:
        with open(head_text, 'r') as headfile:
            with open(foot_text, 'r') as footfile:
                ansimotd.accomodate_motd(testfile, head_file=headfile, foot_file=footfile)
                testfile.seek(0)
                test_motd = testfile.read()

    with open(wrap_headfoot_text, 'r') as reffile:
        reference_motd = reffile.read()

    assert test_motd == reference_motd


def test_accomodate_motd_url(tmpdir, unwrap_text, wrap_indent_url_text, test_url):
    # Copy input text to tmpdir to avoid updating file in example dir
    test_filepath = os.path.join(tmpdir, os.path.basename(unwrap_text))
    shutil.copy(unwrap_text, test_filepath)

    with open(test_filepath, 'r') as testfile:
        ansimotd.accomodate_motd(testfile, foot_link=test_url)
        testfile.seek(0)
        test_motd = testfile.read()

    with open(wrap_indent_url_text, 'r') as reffile:
        reference_motd = reffile.read()

    assert test_motd == reference_motd


def test_accomodate_motd_head_foot_url(tmpdir, unwrap_text, head_text, foot_text, wrap_headfoot_url_text, test_url):
    # Copy input text to tmpdir to avoid updating file in example dir
    test_filepath = os.path.join(tmpdir, os.path.basename(unwrap_text))
    shutil.copy(unwrap_text, test_filepath)

    with open(test_filepath, 'r') as testfile:
        with open(head_text, 'r') as headfile:
            with open(foot_text, 'r') as footfile:
                ansimotd.accomodate_motd(testfile, head_file=headfile, foot_file=footfile, foot_link=test_url)
                testfile.seek(0)
                test_motd = testfile.read()

    with open(wrap_headfoot_url_text, 'r') as reffile:
        reference_motd = reffile.read()

    assert test_motd == reference_motd
