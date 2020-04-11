# encoding: utf-8
"""
:mod:`mybgg.main` - Command-line commands
=========================================

.. module:: mybgg.main
.. moduleauthor:: Rubens Altimari <rubens@altimari.nl>
"""

import codecs
import sys
import locale
import warnings
import argparse

from commands import mybgg_stats, mybgg_owned, mybgg_wishlist, mybgg_designers


def main(args):
    """
    Dispatches commands
    """
    if args.stats:
        mybgg_stats(args)
    if args.owned:
        mybgg_owned(args)
    if args.wishlist:
        mybgg_wishlist(args)
    if args.designers:
        mybgg_designers(args)


if __name__ == '__main__':
    # Accepted arguments & options
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("username", help='username at boardgamegeek.com')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-o", "--owned", help="prints owned games", action="store_true")
    group.add_argument("-w", "--wishlist", help="prints wishlist", action="store_true")
    group.add_argument("-d", "--designers", help="prints designers", action="store_true")
    parser.add_argument("-b", "--bayesian", help="computes average for designers in a Bayesian way", action="store_true")
    group.add_argument("-s", "--stats", help="prints stats", action="store_true")
    parser.add_argument("-r", "--rank", help="ranking to use for games (default: user)", choices=['geek', 'user', 'weight'], default='user')
    parser.add_argument("-p", "--players", help="filter games for # of players", type=int)
    args = parser.parse_args()

    # If Python 2.x
    if sys.version_info.major < 3:
        # Wrap sys.stdout into a StreamWriter to allow writing unicode
        # (and get rid of UnicodeEncodeError when bash piping)
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

    # Remove FutureWarning warnings, contained in the current version of boardgamegeek2 library
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        main(args)
