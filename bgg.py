#!/usr/bin/env python
# encoding: utf-8
"""
bgg.py

pip freeze
-e git+git@github.com:lcosmin/boardgamegeek.git@a4106fd7cd5dd4d59acb054664aabbd266e8c4e9#egg=boardgamegeek2

Created by Rubens Altimari on 2017-07-22.
Demonstrated to Francisco Altimari on 2019-02-20.
Copyright (c) 2017 Rubens Altimari. All rights reserved.
"""

import codecs
import locale
import sys
import warnings
import argparse

from boardgamegeek import BGGClient
from boardgamegeek import api

FIELDS_COLLECTION = ('id', 'name', 'rating', 'owned', 'numplays', 'preordered', 'wishlist', 'wishlist_priority')
FIELDS_GAME = ('designers', 'image', 'thumbnail', 'expansion', 'minplayers', 'maxplayers', 'yearpublished', 'bgg_rank', 'rating_average', 'rating_bayes_average', 'rating_average_weight', 'users_rated')

# Chunk size when calling BGG API to retrieve game list
BGG_CHUNK_SIZE = 500

# Totally arbitrary values for computing the Bayesian average score of a designer (see more remarks in the corresponding code section)
# TODO: find a more "scientific" approach, this is a total guess! :-)
BAYESIAN_ELEMENTS = 5
BAYESIAN_AVERAGE  = 5


def main(args):
    """
    Generates list of games for given BGG username, plus some stats
    """
    if args.stats:
        print_stats(args)
    else:
        collection, games = get_games(args.username)
        if args.owned:
            print_owned(args, collection, games)
        if args.wishlist:
            print_wishlist(args, collection, games)
        if args.designers:
            print_designers(args, collection, games)


def print_owned(args, collection, games):
    """
    List of owned games EXCLUDING expansions
    """
    owned = sorted(
        [item.id for item in collection.values() if item.owned and not games[item.id].expansion],
        key=lambda id: games[id].bgg_rank or 999999
    )
    if args.rank == 'user':
        owned = sorted(owned, key = lambda id: collection[id].rating or 0, reverse=True)
    elif args.rank == 'weight':
        owned = sorted(owned, key = lambda id: games[id].rating_average_weight or 0, reverse=True)
    print('Games Owned: %s (without expansions)\n==========' % len(owned))
    print_games(args, owned, collection, games)


def print_wishlist(args, collection, games):
    """
    Wishlist, ordered by priority (must have, nice to have, etc.)
    """
    if args.rank == 'bgg':
        key = lambda id: games[id].bgg_rank or 999999
    else:
        key = lambda id: collection[id].wishlist_priority
    wishlist = sorted(
        [item.id for item in collection.values() if item.wishlist],
        key=key
    )
    print('Wishlist: %s\n==========' % len(wishlist))
    print_games(args, wishlist, collection, games)


def print_designers(args, collection, games):
    """
    Stats per designer
    """
    owned = [item.id for item in collection.values() if item.owned and not games[item.id].expansion]
    designers = {}
    for id in owned:
        # Gives score to the designer either based on BGG rank or user rating
        score = games[id].rating_bayes_average if args.rank == 'bgg' else collection[id].rating
        try:
            score = float(score)
        except:
            score = 0.0
        # Adds designer to dictionary (if not already there) and increment score
        game = games[id].name
        for designer in games[id].designers:
            entry = designers.setdefault(designer, {'games': [], 'scored_games': 0, 'score_total': 0.0, 'average': 0.0})
            entry['games'].append(game)
            # Updates average only if score is not zero (disregard not scored games)
            if score:
                # Bayesian average: adds BAYESIAN_ELEMENTS of BAYESIAN_AVERAGE to the designer average score,
                # to minimize the effect of computing an average for a small set of elements
                # The intention is to have a higher average if there are *many* games of the same designer
                # with a high score. BGG, for instance, is supposed to add 100 scores of value 5.5 to the
                # BGG geek rating - actual formula is "secret" to avoid manipulation, according to
                # https://www.boardgamegeek.com/wiki/page/BoardGameGeek_FAQ#toc4
                if args.bayesian and entry['scored_games'] == 0:
                    entry['scored_games'] += BAYESIAN_ELEMENTS
                    entry['score_total']  += BAYESIAN_ELEMENTS * BAYESIAN_AVERAGE

                # Computes current average
                entry['scored_games'] += 1
                entry['score_total'] += score
                entry['average'] = entry['score_total']/entry['scored_games']


    # Order designers by average
    top_designers = [{'name': d[0], 'average': d[1]['average'], 'games': d[1]['games']} for d in sorted(
        designers.items(),
        key=lambda e: e[1]['average'],
        reverse=True
    )]

    # List designers
    # TODO: find a way to query OTHER games by these designers from BGG (there's no API call for that)
    print('Designers: %s - %s\n==========' % (len(top_designers), 'https://www.boardgamegeek.com/browse/boardgamedesigner'))
    if args.verbose:
        for designer in top_designers:
            print('%s\n---------' % designer['name'])
            print('\taverage: %s' % designer['average'])
            print('\tgames: %s' % ', '.join(designer['games']))
            print('')
    else:
        print('average name                           games\n')
        for designer in top_designers:
            game_list = ', '.join(designer['games'])
            name = designer['name']
            print('%6.2f %-30.30s %-100.100s' % (
                designer['average'],
                (name[:28] + '..') if len(name) > 30 else name,
                (game_list[:98] + '..') if len(game_list) > 100 else game_list,
            ))


def print_games(args, ids, collection, games):
    """
    Prints list of games in a fixed-column format
    """
    if not args.verbose:
        print(' rank  geek user exp pre name                                     year min max weight\n')

    for id in ids:
        game = games[id]
        item = collection[id]
        # Check if --players parameter was given, and it's within range
        # TODO: create a means to restrict to *exactly* the specified amount of players
        if args.players:
            if not game.minplayers <= args.players <= game.maxplayers:
                continue
        # Tabular or Verbose
        if args.verbose:
            print('%s\n---------' % game.name)
            for field in FIELDS_GAME:
                print('%s: %s' % (field, getattr(game, field)))
            for field in FIELDS_COLLECTION:
                print('%s: %s' % (field, getattr(item, field)))
            print('')
        else:
            print('%5s  %1.2f   %2.2s %3.3s %3.3s %-40.40s %4s  %2.2s  %2.2s   %1.2f' % (
                game.bgg_rank or '',
                game.rating_bayes_average,
                (int(item.rating) if item.rating else '') if item.owned else (item.wishlist_priority or ''),
                ' + ' if game.expansion else '',
                ' > ' if game.preordered else '',
                game.name,
                game.yearpublished,
                game.minplayers,
                game.maxplayers,
                game.rating_average_weight,
            ))


def get_games(username):
    """
    Returns list of games in the collection of the given BGG username
    """
    bgg = BGGClient()
    collection = {item.id: item for item in bgg.collection(username)}
    # games    = {game.id: game for game in bgg.game_list(list(collection.keys()))}

    # Call BGG endpoint in chunks to avoid timeout
    games    = {}
    game_ids = list(collection.keys())
    for start in range(1+(len(game_ids)-1)//BGG_CHUNK_SIZE):
        chunk = game_ids[start*BGG_CHUNK_SIZE : (start+1)*BGG_CHUNK_SIZE]
        games.update({game.id: game for game in bgg.game_list(chunk)})

    # Enrich game list with attributes that are only present on the collections level (for whatever reason...)
    for game_id in game_ids:
        setattr(games[game_id], 'preordered', getattr(collection[game_id],'preordered'))

    # TODO: enrich game info with "best for" value
    # players = [(v.player_number,v.votes_for_best) for v in game.player_number_votes]
    # best = sorted(players, key=lambda tuple: tuple[1])
    # game_dict['best for'] = best[-1][0] if (best and best[-1][1] > 0) else ''

    return collection, games


def get_expansions(ids):
    """
    Returns list of expansions for given list of game IDs
    """
    # TODO: list expansions per game, not counting the ones already in the collection
    # expansions = [e.name for e in game.expansions]
    # game_dict['expansions'] = '\n'.join(expansions)


def print_stats(args):
    """
    Prints some stats about collection
    """
    stats = get_stats(args.username)
    print('{:12.12s}  {:3d}'         .format('Available'  , stats['available']))
    print('  {:12.12s}{:3d} ({:.1%})'.format('Played'     , stats['played'], stats['played_percentage']))
    print('  {:12.12s}{:3d} ({:.1%})'.format('Not Played' , stats['not_played'], stats['not_played_percentage']))
    print('{:12.12s}  {:3d}'         .format('Pre-Ordered', stats['pre_ordered']))
    print('{:12.12s}  {:3d}'         .format('Wishlist'   , stats['wishlist']))


def get_stats(username):
    """
    Returns stats about the collection (just games, not expansions) of a given BGG username
    """
    bgg = BGGClient()
    collection = bgg.collection(
        username,
        subtype='boardgame',
        exclude_subtype='boardgameexpansion'
    )
    stats = {
        'available'   : len([game for game in collection if game.owned and not game.preordered]),
        'played'      : len([game for game in collection if game.rating and game.owned and not game.preordered]),
        'not_played'  : len([game for game in collection if not game.rating and game.owned and not game.preordered]),
        'pre_ordered' : len([game for game in collection if game.preordered]),
        'wishlist'    : len([game for game in collection if game.wishlist]),
    }
    stats['played_percentage'] = stats['played'] / stats['available']
    stats['not_played_percentage'] = stats['not_played'] / stats['available']
    return stats


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
