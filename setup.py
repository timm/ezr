from setuptools import setup

setup(
    name='ezr',
    version='0.1.0',
    license="BSD2",
    py_modules=['ezr'],
    url='https://github.com/timm/ezr',
    author='Tim Menzies',
    author_email='timm@ieee.org',
    description='Semi-supervised explanations for incremental multi-objective optimization',
    install_requires=[],
    entry_points='''
        [console_scripts]
        ezr=ezr:MAIN.main
    ''',
)
