# Following tips from:
# https://www.freecodecamp.org/news/how-to-use-github-as-a-pypi-server-1c3b0d07db2/
# https://dzone.com/articles/executable-package-pip-install
# python setup.py bdist_wheel

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mybgg",
    version="1.9.2",
    # scripts=['mybgg'] ,
    author="Rubens Altimari",
    author_email="rubens@altimari.nl",
    description="A command-line tool to query someone's game collection at boardgamegeek.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dalembertian/mybgg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "boardgamegeek2",
        "requests-cache<=0.5.2",
    ],
    entry_points={
        "console_scripts": [
            "mybgg = mybgg.main:main"
        ],
    },
)
