# encoding: utf-8
"""
.. module:: mybgg
   :synopsis: Uses boardgamegeek2 library to query a BGG user's collection

.. moduleauthor:: Rubens Altimari <rubens@altimari.nl>

pip freeze:
    bgg-api==1.1.13
    build==1.3.0

Install with:
    pip install bgg-api
or:
    pip install -e git+git@github.com:SukiCZ/boardgamegeek.git#egg=bgg-api

Running manually (from parent directory):
    python -m mybgg.main

Installing:
    pip install build
    python -m build
    pip install dist/*.whl
    mybgg --help

Publish to PyPI:
    pip install twine
    twine upload dist/*
"""

from .commands import mybgg_stats, mybgg_owned, mybgg_wishlist, mybgg_designers

# __all__ = ["mybgg_stats", "mybgg_games", "mybgg_owned", "mybgg_wishlist", "mybgg_designers"]
