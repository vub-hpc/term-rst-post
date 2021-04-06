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
Unit tests for term_rst_post.filetools

@author: Alex Domingo (Vrije Universiteit Brussel)
"""

import os
import pytest
import shutil

from term_rst_post import filetools


@pytest.fixture
def ablog_newspost_file(exampledir):
    return os.path.join(exampledir, 'ablog_newspost_simple.rst')


def test_valid_dirpath(tmpdir):
    assert filetools.valid_dirpath(tmpdir) == f"{tmpdir}"


def test_resolve_path(tmpdir):
    test_filename = 'resolve.test'
    test_abspath = os.path.join(tmpdir, test_filename)

    os.chdir(tmpdir)
    assert filetools.resolve_path(test_filename) == test_abspath


@pytest.mark.parametrize(
    'test_link',
    [
        ('../../test/file', 'test/file'),
        ('./test/file', 'test/file'),
        ('/test', 'test'),
        ('.././../test', 'test'),
        ('test/../file', 'test/../file'),
        ('/test/../file', 'test/../file'),
    ],
)
def test_inward_path(test_link):
    example_link, reference_path = test_link
    test_path = filetools.inward_path(example_link)
    assert test_path == reference_path


def test_change_file_extension(tmpdir, ablog_newspost_file):
    test_path = os.path.join(tmpdir, ablog_newspost_file)
    test_html = filetools.change_file_extension(test_path, '.html')

    reference_html = os.path.basename(test_path).split('.')[0] + '.html'

    assert f"{test_html}" == reference_html


def test_change_file_extension_fullpath(tmpdir, ablog_newspost_file):
    test_path = os.path.join(tmpdir, ablog_newspost_file)
    test_html = filetools.change_file_extension(test_path, '.html', True)

    reference_html = test_path.split('.')[0] + '.html'

    assert f"{test_html}" == reference_html


def test_fileobj_extension(ablog_newspost_file):
    with open(ablog_newspost_file) as testfile:
        assert filetools.fileobj_extension(testfile) == '.rst'


@pytest.mark.parametrize(
    'test_joinable_paths',
    [
        ('apple/pear', 'apple/pear/test.rst', 'apple/pear/test.rst'),
        ('apple/pear', 'banana/apple/pear/test.rst', 'apple/pear/test.rst'),
        ('apple/pear', 'apple/pear/grape/test.rst', 'apple/pear/grape/test.rst'),
        ('apple/pear', 'banana/apple/pear/grape/test.rst', 'apple/pear/grape/test.rst'),
        ('apple/pear/orange', 'apple/pear/test.rst', 'apple/pear/test.rst'),
        ('apple/pear/orange', 'banana/apple/pear/test.rst', 'apple/pear/test.rst'),
        ('apple/pear/orange', 'apple/pear/grape/test.rst', 'apple/pear/grape/test.rst'),
        ('apple/pear/orange', 'banana/apple/pear/grape/test.rst', 'apple/pear/grape/test.rst'),
        ('cherry/apple/pear/orange', 'apple/pear/test.rst', 'cherry/apple/pear/test.rst'),
        ('cherry/apple/pear/orange', 'banana/apple/pear/test.rst', 'cherry/apple/pear/test.rst'),
        ('cherry/apple/pear/orange', 'apple/pear/grape/test.rst', 'cherry/apple/pear/grape/test.rst'),
        ('cherry/apple/pear/orange', 'banana/apple/pear/grape/test.rst', 'cherry/apple/pear/grape/test.rst'),
        ('cherry/apple/pear/orange', 'apple/kiwi/pear/test.rst', 'cherry/apple/pear/test.rst'),
        ('cherry/apple/pear/orange', 'banana/apple/kiwi/pear/test.rst', 'cherry/apple/pear/test.rst'),
        ('cherry/apple/pear/orange', 'apple/kiwi/pear/grape/test.rst', 'cherry/apple/pear/grape/test.rst'),
        ('cherry/apple/pear/orange', 'banana/apple/kiwi/pear/grape/test.rst', 'cherry/apple/pear/grape/test.rst'),
        ('apple/pear/index.html', 'apple/pear/grape/test.rst', 'apple/pear/grape/test.rst'),
        ('cherry/apple/pear/orange/index.html', 'banana/apple/pear/grape/test.rst', 'cherry/apple/pear/grape/test.rst'),
    ],
)
def test_common_path_join(test_joinable_paths):
    left_path, right_path, reference_path = test_joinable_paths
    test_join_path = filetools.common_path_join(left_path, right_path)
    assert test_join_path == reference_path


def test_rst_path_from_html_link(tmpdir, ablog_newspost_file):
    # Copy RST to temp dir
    tmpexample = os.path.join(tmpdir, 'examples')
    os.makedirs(tmpexample)
    shutil.copy(ablog_newspost_file, tmpexample)

    # Locate RST from HTML link
    html_link = '../../examples/ablog_newspost_simple'
    html_file = os.path.join(tmpdir, '_website', 'examples', 'ablog_newsfeed.html')
    rst_file = filetools.rst_path_from_html_link(html_link, html_file)

    reference_rst = os.path.join(tmpexample, os.path.basename(ablog_newspost_file))

    assert f"{rst_file}" == reference_rst
