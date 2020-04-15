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

from .commands import mybgg_stats, mybgg_owned, mybgg_wishlist, mybgg_designers


def execute_command(args):
    if args.stats:
        mybgg_stats(args.username)
    if args.owned:
        mybgg_owned(args.username, args.rank, args.players, args.verbose)
    if args.wishlist:
        mybgg_wishlist(args.username, args.rank, args.players, args.verbose)
    if args.designers:
        mybgg_designers(args.username, args.rank, args.bayesian, args.verbose)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("username", help='username at boardgamegeek.com')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--stats", help="prints stats", action="store_true")
    group.add_argument("-o", "--owned", help="prints owned games", action="store_true")
    group.add_argument("-w", "--wishlist", help="prints wishlist", action="store_true")
    parser.add_argument("-r", "--rank", help="ranking to use for games (default: user)", choices=['geek', 'user', 'weight'], default='user')
    parser.add_argument("-p", "--players", help="filter games for # of players", type=int)
    group.add_argument("-d", "--designers", help="prints designers", action="store_true")
    parser.add_argument("-b", "--bayesian", help="computes average for designers in a Bayesian way", action="store_true")
    args = parser.parse_args()

    # If Python 2.x
    if sys.version_info.major < 3:
        # Wrap sys.stdout into a StreamWriter to allow writing unicode
        # (and get rid of UnicodeEncodeError when bash piping)
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

    # Remove FutureWarning warnings, contained in the current version of boardgamegeek2 library
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        execute_command(args)

if __name__ == '__main__':
    main()