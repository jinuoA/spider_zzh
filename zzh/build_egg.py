#! /usr/bin/env python
#-*-coding:utf-8 -*-
import glob
import os
import sys
import tempfile
import shutil
import datetime
from os.path import join
from subprocess import check_call

import configparser
from scrapy.utils.python import retry_on_eintr


def build_project(project):
    egg = build_egg(project)
    print('Built %(project)s into %(egg)s' % {'egg': egg, 'project': project})
    return egg


_SETUP_PY_TEMPLATE = \
    """# Automatically created by: gerapy
from setuptools import setup, find_packages
setup(
    name='%(project)s',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy':['settings=%(settings)s']},
)"""



def config(path, section, option, name='scrapy.cfg', default=None):
    try:
        cf = configparser.ConfigParser()
        cfg_path = join(path, name)
        cf.read(cfg_path)
        return cf.get(section, option)
    except configparser.NoOptionError:
        return default

def create_default_setup_py(path, **kwargs):
    with open(join(path, 'setup.py'), 'w') as f:
        print(kwargs)
        file = _SETUP_PY_TEMPLATE % kwargs
        f.write(file)
        f.close()

def find_egg(path):
    items = os.listdir(path)
    for name in items:
        if name.endswith(".egg"):
            return name
    return None


# 构建Egg
def build_egg(project):
    work_path = os.getcwd()
    try:
        path = os.path.abspath(join(os.getcwd()))
        project_path = join(path)
        os.chdir(project_path)
        settings = config(project_path, 'settings', 'default')
        create_default_setup_py(project_path, settings=settings, project=project)
        d = tempfile.mkdtemp(prefix="zzh-")
        o = open(os.path.join(d, "stdout"), "wb")
        e = open(os.path.join(d, "stderr"), "wb")
        retry_on_eintr(check_call, [sys.executable, 'setup.py', 'clean', '-a', 'bdist_egg', '-d', d],
                       stdout=o, stderr=e)
        o.close()
        e.close()
        egg = glob.glob(os.path.join(d, '*.egg'))[0]
        # Delete Origin file
        if find_egg(project_path):
            os.remove(join(project_path, find_egg(project_path)))
        shutil.move(egg, project_path)
        return join(project_path, find_egg(project_path))
    except Exception as e:
        print(e.args)
    finally:
        os.chdir(work_path)



build_project('zzh')