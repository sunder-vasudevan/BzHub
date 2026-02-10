from setuptools import setup

APP = ['word_formatter.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['docx', 'lxml'],
    'iconfile': None,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
