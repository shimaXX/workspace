# coding: utf-8
# python setup.py py2exe �R���\�[��������s

from distutils.core import setup
import py2exe
from glob import glob


data_files = [("microsoft.vc90.crt",
               ["microsoft.vc90.crt.manifest_"] + glob(r'msvc*90.dll'))]

setup(windows=['excel_operate.py'],
      options={"py2exe":{"includes":["sip"]}},
      data_files=data_files)