# encoding: utf-8
"""
:mod:`mybgg.main` - Command-line commands
=========================================

.. module:: mybgg.main
.. moduleauthor:: Rubens Altimari <rubens@altimari.nl>

Use python -m mybgg.maim from parent directory if running manually
"""

import os
import codecs
import sys
import locale
import warnings
import argparse

from .commands import mybgg_stats, mybgg_owned, mybgg_wishlist, mybgg_designers


def execute_command(args):
    access_token = os.getenv('BGG_ACCESS_TOKEN', '')
    print(f'Using BGG Access Token: {access_token} (export BGG_ACCESS_TOKEN)')
    if args.stats:
        mybgg_stats(access_token, args.username)
    if args.owned:
        mybgg_owned(access_token, args.username, args.rank, args.players, args.exclusive, args.verbose)
    if args.wishlist:
        mybgg_wishlist(access_token, args.username, args.rank, args.players, args.exclusive, args.verbose)
    if args.designers:
        mybgg_designers(access_token, args.username, args.rank, args.bayesian, args.verbose)

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
    parser.add_argument("-x", "--exclusive", help="looks for exact match on # of players (best for)", action="store_true")
    group.add_argument("-d", "--designers", help="prints designers", action="store_true")
    parser.add_argument("-b", "--bayesian", help="computes average for designers in a Bayesian way", action="store_true")
    args = parser.parse_args()

    execute_command(args)

if __name__ == '__main__':
    main()