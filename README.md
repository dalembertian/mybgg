# MYBGG

Simple script to query someone's collection of boardgames at boardgamegeek.com

### Prerequisites

* Works with both Python 2 and 3
* Installs [boardgamegeek v2](https://github.com/lcosmin/boardgamegeek/) as a dependency

### Installing

Just install from Github and run **mybgg** from the command line.

```
pip install git+https://github.com/dalembertian/mybgg.git

$ mybgg -h

usage: mybgg [-h] [-v] (-o | -w | -d) [-b] [-r {bgg,user}] [-p PLAYERS]
              username

positional arguments:
  username              username at boardgamegeek.com

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -s, --stats           prints stats
  -o, --owned           prints owned games
  -w, --wishlist        prints wishlist
  -r {geek,user,weight}, --rank {geek,user,weight}
                        ranking to use for games (default: user)
  -p PLAYERS, --players PLAYERS
                        filter games for # of players
  -d, --designers       prints designers
  -b, --bayesian        computes average for designers in a Bayesian way
```

## Examples

My collection, ordered by the BGG rank:

```
$ mybgg dalembertian -o -r bgg

Games Owned: 118 (without expansions)
==========
  BGG  rate user name                                     year min max

    1  8.62      Gloomhaven                               2017   1   4
    2  8.50      Pandemic Legacy: Season 1                2015   2   4
    3  8.31      Through the Ages: A New Story of Civiliz 2015   2   4
    4  8.20    8 Twilight Struggle                        2005   2   2
    8  8.10      Terra Mystica                            2012   2   5
   11  8.01   10 7 Wonders Duel                           2015   2   2
                 .
                 .
```

My wishlist, ordered by my own priorities:

```
$ mybgg dalembertian -w

Wishlist: 36
==========
  BGG  rate user name                                     year min max

   42  7.72    1 Azul                                     2017   2   4
  126  7.36    1 Lisboa                                   2017   1   4
  683  6.65    2 Ambush!                                  1983   1   1
 8385  5.55    2 Djambi                                   1968   3   4
  852  6.52    2 The Lost Expedition                      2017   1   5
  645  6.69    2 Rivals for Catan                         2010   2   2
  162  7.29    2 Sagrada                                  2017   1   4
  179  7.25    3 Agricola: All Creatures Big and Small    2012   2   2
                 .
                 .
```

Some stats about my collection (excluding expansions):

```
$ mybgg dalembertian -s

Available     153
  Played      105 (68.6%)
  Not Played   48 (31.4%)
Pre-Ordered    12
Wishlist       35

```

List of designers of the games I have, ordered by the average of my rank (disregarding non-scored games):

```
$ mybgg dalembertian -d

Designers: 118 - https://www.boardgamegeek.com/browse/boardgamedesigner
==========
average name                           games

 10.00 Antoine Bauza                  7 Wonders Duel
 10.00 Uwe Rosenberg                  Agricola, Caverna: Cave vs Cave, Le Havre, Patchwork
 10.00 Lukas Litzsinger               Android: Netrunner
 10.00 Friedemann Friese              Fast Forward: FEAR, Friday
 10.00 Matt Leacock                   Forbidden Island, Pandemic Legacy: Season 1
  9.50 Emiliano Sciarra               BANG!, BANG! The Duel
  9.00 Bruno Cathala                  7 Wonders Duel, Five Tribes, Mr. Jack Pocket, Raptor
       .
       .
```

Same, but ordered by a Bayesian average (similar to the BGG geek rank: the more higher score games, the better):

```
$ mybgg dalembertian -d -b

Designers: 118 - https://www.boardgamegeek.com/browse/boardgamedesigner
==========
average name                           games

  6.38 Tim Fowers                     Burgle Bros., Fugitive, Hardback, Now Boarding, Paperback
  6.29 Emiliano Sciarra               BANG!, BANG! The Duel
  6.14 Bruno Cathala                  7 Wonders Duel, Five Tribes, Mr. Jack Pocket, Raptor
  6.14 Vlaada Chvátil                 Codenames, Codenames Duet, Galaxy Trucker, Mage Knight Board Game, Through the Ages: A New Story o..
  6.00 Alan R. Moon                   Ticket to Ride, Ticket to Ride: The Card Game
  5.89 Andrew Looney                  Fluxx, Loonacy, Monty Python Fluxx, Pyramid Arcade, Seven Dragons
  5.86 Richard Garfield               Android: Netrunner, Magic: The Gathering
  5.83 Antoine Bauza                  7 Wonders Duel
       .
       .
```

So I have 5 people playing tonight, what can we play? (First the ones I played and rated, then the ones I never played)

```
 $ mybgg dalembertian -o -p 5

 Games Owned: 118 (without expansions)
==========
  BGG  rate user name                                     year min max

   44  7.70   10 Codenames                                2015   2   8
  125  7.37   10 Ticket to Ride                           2004   2   5
  184  7.24    9 Small World                              2009   2   5
  296  7.05    9 Colt Express                             2014   2   6
                 .
                 .
    8  8.10      Terra Mystica                            2012   2   5
   17  7.92      Agricola                                 2007   1   5
   21  7.89      Mansions of Madness: Second Edition      2016   1   5
   32  7.80      Kingdom Death: Monster                   2015   1   6
                 .
                 .
```

## Authors

* **Rubens Altimari** - [dalembertian](https://github.com/dalembertian)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
