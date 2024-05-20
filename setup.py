from setuptools import setup,find_packages

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='ezr',
    description='a less is more approach to sequential model optimization',
    long_description=long_description,
    version='0.1.0',
    license="BSD2",
    py_modules=['ezr'],
    url='https://github.com/timm/ezr',
    author='Tim Menzies',
    author_email='timm@ieee.org',
    install_requires=[],
    packages=find_packages(),
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: BSD License',
    'Development Status :: 2 - Pre-Alpha',
    'Operating System :: OS Independent',
    ],
    entry_points='''
        [console_scripts]
        ezr=ezr:main
    ''',
)
