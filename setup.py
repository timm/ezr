from setuptools import setup, find_packages

setup(
    name='ezr',
    version='0.2.0',
    license="BSD-2-Clause",
    description='Semi-supervised explanations for incremental multi-objective optimization',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Tim Menzies',
    author_email='timm@ieee.org',
    url='https://github.com/timm/ezr',

    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Education',
    ],

    entry_points={
        'console_scripts': [
            'ezr=ezr.__main__:main',  # <--- calls main() in __main__.py
        ],
    },
)


