# WS API Overview

_optional_, **for both directions**, g = game, p = player

## Pre-game stage
| to client from server | to server from client |
| :-- | --: |
|  | command: login, nick: foobar |
| _error: 1001_ |  |
| player_id: 6 |  |
| games: [{id: 1, players: [Foo, Bar, Joe]}, {id: 2, players: [Too, True, Mrazek]}] | |
|  | command: select, game_id: 2 |
| _error: 1002_ | |

## Pre-start stage
| to client from server | to server from client |
| :-- | --: |
| **command: player\_ready, player\_id: 3** | |
| **command: player\_add, id: 3, game_id: 2, color: #abcdef** | |
| command: start, time: 10 | |
| command: init, entity: Planet, values: {id: 1, x: 1024, y: 512, owner_id: 6, size: (0, 10, int)} | |

## Game stage
| to client from server | to server from client |
| :-- | --: |
| command: action, entity: Ship, id: 6, values: {params for this action} | |
| command: action, entity: Planet, id: 6, values: {capturer_id: 3, action: capture, previous_owner_id: 33} | |

## ship actions
##### init
creating new ship
##### set
any of the parameters to set (x, y, hp) 
##### follow
ship want follow another enemy ship - following_id
##### disfollow
ship want stop actually following
##### move
ship want move to abs. position - x, y (maybe be used before recycling)
##### recycle
recycle to planet - planet_id


### error codes & messages
| error code | error message |
| --- | --- |
| 1001 | nick has been already used |
| 1002 | this game has been already started |
