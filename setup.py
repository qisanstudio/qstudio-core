#! /usr/bin/env python
# -*- coding: UTF-8 -*-
try:
    # work-around to avoid "setup.py test" error
    # see: http://bugs.python.org/issue15881#msg170215
    import multiprocessing
    assert multiprocessing
except ImportError:
    pass

import os
import setuptools


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(filename):
    with open(os.path.join(os.getcwd(),
                           'requirements',
                           filename)) as fp:
        return filter(None, [strip_comments(l)
                             for l in fp.readlines()])


setup_params = dict(
    name="qstudio-core",
    url="http://wiki.yimiqisan.com/",
    version='1.0',
    author="qisan",
    author_email="qisanstudio@gmail.com",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=reqs('install.txt'),
    namespace_packages=['studio'])

if __name__ == '__main__':
    setuptools.setup(**setup_params)
