# BGG

Simple script to query someone's collection of boardgames at boardgamegeek.com

### Prerequisites

* [Python 3.6](https://docs.python.org/3/)
* [boardgamegeek](https://github.com/lcosmin/boardgamegeek/) - A Python API for boardgamegeek.com

### Installing

Just install the boardgamegeek2 library and run **bgg.py** from the command line.

```
pip install -e git+git@github.com:lcosmin/boardgamegeek.git#egg=boardgamegeek2

$ ./bgg.py -h
usage: bgg.py [-h] [-v] (-o | -w | -d) [-r {bgg,user}] [-p PLAYERS] username

positional arguments:
  username              username at boardgamegeek.com

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -o, --owned           prints owned games
  -w, --wishlist        prints wishlist
  -d, --designers       prints designers
  -r {bgg,user}, --rank {bgg,user}
                        ranking to use for games (default: user)
  -p PLAYERS, --players PLAYERS
                        filter games for # of players
```

## Examples

My collection, ordered by the BGG rank:

```
$ ./bgg.py dalembertian -o -r bgg

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
$ ./bgg.py dalembertian -w

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

List of designers of the games I have, ordered by "weight" (sum of my rates):

```
$ ./bgg.py dalembertian -d

Designers: 118 - https://www.boardgamegeek.com/browse/boardgamedesigner
==========
weight name                           games

 29.00 Andrew Looney                  Fluxx, Loonacy, Monty Python Fluxx, Pyramid Arcade, Seven Dragons                                   
 28.00 Tim Fowers                     Burgle Bros., Fugitive, Hardback, Now Boarding, Paperback                                           
 21.00 Vlaada Chvátil                 Codenames, Codenames Duet, Galaxy Trucker, Mage Knight Board Game, Through the Ages: A New Story o..
       .
       .
```

So I have 5 people playing tonight, what can we play? (First the ones I played and rated, then the ones I never played)

```
 $ ./bgg.py dalembertian -o -p 5

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

* **Rubens Altimari** - *Initial work* - [dalembertian](https://github.com/dalembertian)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
