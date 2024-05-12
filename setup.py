from setuptools import setup,find_packages

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
    packages=find_packages(),
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: BSD License',
    'Development Status :: 2 - Pre-Alpha',
    'Operating System :: OS Independent',
    ],
    entry_points='''
        [console_scripts]
        ezr=ezr:MAIN.main
    ''',
)
