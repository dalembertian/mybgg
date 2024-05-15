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
FIELDS_GAME = ('designers', 'image', 'thumbnail', 'expansion', 'minplayers', 'maxplayers', 'yearpublished', 'bgg_rank',
               'rating_average', 'rating_bayes_average', 'rating_average_weight', 'users_rated')

# Chunk size when calling BGG API to retrieve game list
BGG_CHUNK_SIZE = 500

# XMLAPI2 parameters
BGG_TIMEOUT = 10 # previous = 30; default = 15 - Total timeout (in seconds) for a request)
BGG_RETRIES =  8 # previous =  6; default =  3 - Amount of retries before giving up
BGG_DELAY   =  1 # previous =  3; default =  5 - Interval (in seconds) between retries, each time mutlitplying by 1.5

# Totally arbitrary values for computing the Bayesian average score of a designer (see more remarks in the corresponding code section)
# TODO: find a more "scientific" approach, this is a total guess! :-)
BAYESIAN_ELEMENTS = 5
BAYESIAN_AVERAGE  = 7


def get_collection(username):
    """
    Return collection (list of games) for a given user
    """
    # bgg = BGGClient(cache=CacheBackendNone())
    bgg = BGGClient(timeout=BGG_TIMEOUT, retries=BGG_RETRIES, retry_delay=BGG_DELAY)
    bgg_collection = bgg.collection(username)
    collection = {item.id: item for item in bgg_collection}
    return collection

def get_games(game_ids):
    """
    Return game details (non-user related) for a list of game IDs
    """
    bgg = BGGClient(timeout=BGG_TIMEOUT, retries=BGG_RETRIES, retry_delay=BGG_DELAY)

    # Call BGG endpoint in chunks to avoid timeout
    games = {}
    for start in range(1 + (len(game_ids) - 1) // BGG_CHUNK_SIZE):
        chunk = game_ids[start * BGG_CHUNK_SIZE: (start + 1) * BGG_CHUNK_SIZE]
        bgg_game_list = bgg.game_list(chunk)
        games.update({game.id: game for game in bgg_game_list})

    for game_id in game_ids:
        # Enrich game list with attributes that are only present on the collections level
        # setattr(games[game_id], 'preordered', getattr(collection[game_id], 'preordered'))
        # Add "best for X players" attribute for each game
        results = games[game_id].suggested_players['results']
        suggestions = [(key, results[key]['best_rating']) for key in results]
        best = sorted(suggestions, key=lambda tuple: tuple[1])
        setattr(games[game_id], 'best_players', int(best[-1][0].strip('+')) if best and best[-1] else 0)

    return games

def get_collection_and_games(username):
    """
    Returns list of games in the collection of the given BGG username
    """
    collection = get_collection(username)
    games = get_games(list(collection.keys()))
    return collection, games

def mybgg_owned(username, rank, players, exclusive, verbose):
    """
    List of owned games EXCLUDING expansions
    """
    collection, games = get_collection_and_games(username)

    owned = sorted(
        [item.id for item in collection.values() if item.owned and not games[item.id].expansion],
        key=lambda id: games[id].bgg_rank or 999999
    )
    if rank == 'user':
        owned = sorted(owned, key=lambda id: collection[id].rating or 0, reverse=True)
    elif rank == 'weight':
        owned = sorted(owned, key=lambda id: games[id].rating_average_weight or 0, reverse=True)
    print('Games Owned: %s (without expansions)\n==========' % len(owned))
    print_games(owned, collection, games, players, exclusive, verbose)

def mybgg_wishlist(username, rank, players, exclusive, verbose):
    """
    Wishlist, ordered by priority (must have, nice to have, etc.)
    """
    collection, games = get_collection_and_games(username)

    if rank == 'bgg':
        key = lambda id: games[id].bgg_rank or 999999
    else:
        key = lambda id: collection[id].wishlist_priority
    wishlist = sorted(
        [item.id for item in collection.values() if item.wishlist],
        key=key
    )
    print('Wishlist: %s\n==========' % len(wishlist))
    print_games(wishlist, collection, games, players, exclusive, verbose)

def mybgg_designers(username, rank, bayesian, verbose):
    """
    Stats per designer
    """
    collection, games = get_collection_and_games(username)
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
                entry['average'] = entry['score_total'] / entry['scored_games']

    # Order designers by average
    top_designers = [{'name': d[0], 'average': d[1]['average'], 'games': d[1]['games']} for d in sorted(
        designers.items(),
        key=lambda e: e[1]['average'],
        reverse=True
    )]

    # List designers
    # TODO: find a way to query OTHER games by these designers from BGG (there's no API call for that)
    print('Designers: %s - %s\n==========' % (
        len(top_designers), 'https://www.boardgamegeek.com/browse/boardgamedesigner'))
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
            print('%5.5s %-30.30s %-100.100s' % (
                '%5.2f' % designer['average'] if designer['average'] else '',
                (name[:28] + '..') if len(name) > 30 else name,
                (game_list[:98] + '..') if len(game_list) > 100 else game_list,
            ))

def print_games(ids, collection, games, players, exclusive, verbose):
    """
    Prints list of games in a fixed-column format
    """
    if not verbose:
        print(' rank  geek  user exp pre name                                     year min max best weight\n')

    for id in ids:
        game = games[id]
        item = collection[id]
        # Check if --players parameter was given, and it's within range
        # TODO: create a means to restrict to *exactly* the specified amount of players
        if players:
            if exclusive:
                if game.best_players != players:
                    continue
            else:
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
            print('%5s  %4.4s  %4.4s %3.3s %3.3s %-40.40s %4s  %2.2s  %2.2s  %3.3s   %1.2f' % (
                game.bgg_rank or '',
                '%1.2f' % game.rating_bayes_average if game.rating_bayes_average else '',
                ('%2.1f' % item.rating if item.rating else '') if item.owned else (item.wishlist_priority or ''),
                ' + ' if game.expansion else '',
                ' > ' if item.preordered else '',
                game.name,
                game.yearpublished,
                game.minplayers,
                game.maxplayers,
                game.best_players,
                game.rating_average_weight,
            ))

def get_boardgames_and_expansions(username):
    """
    Returns separate lists for boardgames and expansions of a given BGG username
    """
    bgg = BGGClient(timeout=BGG_TIMEOUT, retries=BGG_RETRIES, retry_delay=BGG_DELAY)
    boardgames = bgg.collection(
        username,
        subtype='boardgame',
        exclude_subtype='boardgameexpansion',
    )
    expansions = bgg.collection(
        username,
        subtype='boardgameexpansion',
    )
    return boardgames, expansions

def calculate_stats(boardgames, expansions):
    """
    Returns stats about the collection
    """
    stats = {
        'collection':  len([game for game in boardgames if game.owned]) + len([exp for exp in expansions if exp.owned]),
        'available':   len([game for game in boardgames if game.owned and not game.preordered]),
        'played':      len([game for game in boardgames if game.rating and game.owned and not game.preordered]),
        'not_played':  len([game for game in boardgames if not game.rating and game.owned and not game.preordered]),
        'expansions':  len([exp  for exp  in expansions if exp.owned and not exp.preordered]),
        'pre_ordered': len([game for game in boardgames if game.owned and game.preordered]) +
                       len([exp  for exp  in expansions if exp.owned and exp.preordered]),
        'prev_owned':  len([game for game in boardgames if game.prev_owned]) +
                       len([exp  for exp  in expansions if exp.prev_owned]),
        'for_trade':   len([game for game in boardgames if game.for_trade]) +
                       len([exp  for exp  in expansions if exp.for_trade]),
        'wishlist':    len([game for game in boardgames if game.wishlist]) +
                       len([exp  for exp  in expansions if exp.wishlist]),
    }
    stats['played_percentage'] = '{:.1%}'.format(stats['played'] / stats['available'])
    stats['not_played_percentage'] = '{:.1%}'.format(stats['not_played'] / stats['available'])
    return stats

def get_stats(username):
    """
    Returns stats about the collection of a given BGG username
    """
    boardgames, expansions = get_boardgames_and_expansions(username)
    stats = calculate_stats(boardgames, expansions)
    return stats

def mybgg_stats(username):
    """
    Prints some stats about collection
    """
    stats = get_stats(username)
    print('{:12.12s}  {:3d}'.format('Collection', stats['collection']))
    print('{:12.12s}  {:3d}'.format('Boardgames', stats['available']))
    print('  {:12.12s}{:3d} ({:>6.6s})'.format('Played', stats['played'], stats['played_percentage']))
    print('  {:12.12s}{:3d} ({:>6.6s})'.format('Not Played', stats['not_played'], stats['not_played_percentage']))
    print('{:12.12s}  {:3d}'.format('Expansions', stats['expansions']))
    print('{:12.12s}  {:3d}'.format('Pre-Ordered', stats['pre_ordered']))
    print('{:12.12s}  {:3d}'.format('Prev. Owned', stats['prev_owned']))
    print('{:12.12s}  {:3d}'.format('For Trade', stats['for_trade']))
    print('{:12.12s}  {:3d}'.format('Wishlist', stats['wishlist']))

def get_plays(username):
    """
    Returns list of all plays (game played on a given date) plus all play dates (total amount of plays per date)
    """
    # TODO: limit amount of plays retrieved
    bgg = BGGClient(timeout=BGG_TIMEOUT, retries=BGG_RETRIES, retry_delay=BGG_DELAY)
    plays = bgg.plays(username)

    dates = {}
    for play in plays.plays:
        dates[play.date] = dates.get(play.date, 0) + play.quantity

    return plays.plays, dates

def get_expansions(ids):
    """
    Returns list of expansions for given list of game IDs
    """
    # TODO: list expansions per game, not counting the ones already in the collection
    # expansions = [e.name for e in game.expansions]
    # game_dict['expansions'] = '\n'.join(expansions)
