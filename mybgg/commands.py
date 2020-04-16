# encoding: utf-8
"""
:mod:`mybgg.commands` - Main commands
=========================================

pip freeze:
    boardgamegeek2==1.0.1

Install with:
    pip install boardgamegeek2
or:
    pip install -e git+git@github.com:lcosmin/boardgamegeek.git#egg=boardgamegeek2

.. module:: mybgg.main
   :synopsis: Uses boardgamegeek2 library to query a BGG user's collection

.. moduleauthor:: Rubens Altimari <rubens@altimari.nl>
"""

# In case this is still Python 2.x
from __future__ import division

from boardgamegeek import BGGClient, CacheBackendNone

FIELDS_COLLECTION = ('id', 'name', 'rating', 'owned', 'numplays', 'preordered', 'wishlist', 'wishlist_priority')
FIELDS_GAME = ('designers', 'image', 'thumbnail', 'expansion', 'minplayers', 'maxplayers', 'yearpublished', 'bgg_rank', 'rating_average', 'rating_bayes_average', 'rating_average_weight', 'users_rated')

# Chunk size when calling BGG API to retrieve game list
BGG_CHUNK_SIZE = 500

# Totally arbitrary values for computing the Bayesian average score of a designer (see more remarks in the corresponding code section)
# TODO: find a more "scientific" approach, this is a total guess! :-)
BAYESIAN_ELEMENTS = 5
BAYESIAN_AVERAGE  = 5


def mybgg_stats(username):
    """
    Prints some stats about collection
    """
    stats = get_stats(username)
    print('{:12.12s}  {:3d}'           .format('Available'  , stats['available']))
    print('  {:12.12s}{:3d} ({:>6.6s})'.format('Played'     , stats['played'], stats['played_percentage']))
    print('  {:12.12s}{:3d} ({:>6.6s})'.format('Not Played' , stats['not_played'], stats['not_played_percentage']))
    print('{:12.12s}  {:3d}'           .format('Pre-Ordered', stats['pre_ordered']))
    print('{:12.12s}  {:3d}'           .format('Wishlist'   , stats['wishlist']))


def get_stats(username):
    """
    Returns stats about the collection (just games, not expansions) of a given BGG username
    """
    bgg = BGGClient(cache=CacheBackendNone())
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
    stats['played_percentage']     = '{:.1%}'.format(stats['played'] / stats['available'])
    stats['not_played_percentage'] = '{:.1%}'.format(stats['not_played'] / stats['available'])
    return stats


def get_games(username):
    """
    Returns list of games in the collection of the given BGG username
    """
    bgg = BGGClient(cache=CacheBackendNone())
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


def mybgg_owned(username, rank, players, verbose):
    """
    List of owned games EXCLUDING expansions
    """
    collection, games = get_games(username)

    owned = sorted(
        [item.id for item in collection.values() if item.owned and not games[item.id].expansion],
        key=lambda id: games[id].bgg_rank or 999999
    )
    if rank == 'user':
        owned = sorted(owned, key = lambda id: collection[id].rating or 0, reverse=True)
    elif rank == 'weight':
        owned = sorted(owned, key = lambda id: games[id].rating_average_weight or 0, reverse=True)
    print('Games Owned: %s (without expansions)\n==========' % len(owned))
    print_games(owned, collection, games, players, verbose)


def mybgg_wishlist(username, rank, players, verbose):
    """
    Wishlist, ordered by priority (must have, nice to have, etc.)
    """
    collection, games = get_games(username)

    if rank == 'bgg':
        key = lambda id: games[id].bgg_rank or 999999
    else:
        key = lambda id: collection[id].wishlist_priority
    wishlist = sorted(
        [item.id for item in collection.values() if item.wishlist],
        key=key
    )
    print('Wishlist: %s\n==========' % len(wishlist))
    print_games(wishlist, collection, games, players, verbose)


def mybgg_designers(username, rank, bayesian, verbose):
    """
    Stats per designer
    """
    collection, games = get_games(username)    
    owned = [item.id for item in collection.values() if item.owned and not games[item.id].expansion]

    designers = {}
    for id in owned:
        # Gives score to the designer either based on BGG rank or user rating
        score = games[id].rating_bayes_average if rank == 'bgg' else collection[id].rating
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
                if bayesian and entry['scored_games'] == 0:
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
    if verbose:
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


def print_games(ids, collection, games, players, verbose):
    """
    Prints list of games in a fixed-column format
    """
    if not verbose:
        print(' rank  geek user exp pre name                                     year min max weight\n')

    for id in ids:
        game = games[id]
        item = collection[id]
        # Check if --players parameter was given, and it's within range
        # TODO: create a means to restrict to *exactly* the specified amount of players
        if players:
            if not game.minplayers <= players <= game.maxplayers:
                continue
        # Tabular or Verbose
        if verbose:
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


def get_expansions(ids):
    """
    Returns list of expansions for given list of game IDs
    """
    # TODO: list expansions per game, not counting the ones already in the collection
    # expansions = [e.name for e in game.expansions]
    # game_dict['expansions'] = '\n'.join(expansions)
