# encoding: utf-8
"""
.. module:: mybgg
   :synopsis: Uses boardgamegeek2 library to query a BGG user's collection

.. moduleauthor:: Rubens Altimari <rubens@altimari.nl>
"""

from .commands import mybgg_stats, mybgg_games, mybgg_owned, mybgg_wishlist, mybgg_designers

__all__ = ["mybgg_stats", "mybgg_games", "mybgg_owned", "mybgg_wishlist", "mybgg_designers"]

__import__('pkg_resources').declare_namespace(__name__)
