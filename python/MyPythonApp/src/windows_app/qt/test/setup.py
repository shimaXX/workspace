# coding: utf-8
# python setup.py py2exe コンソールから実行

from distutils.core import setup
import py2exe
from glob import glob


data_files = [("microsoft.vc90.crt",
               ["microsoft.vc90.crt.manifest"] + glob(r'msvc*90.dll'))]

setup(windows=['qt_test.py'],
      options={"py2exe":{"includes":["sip"]}},
      data_files=data_files)