# WS API Overview

_optional_, **for both directions**, g = game, p = player

### Pre-game stage
| to client from server | to server from client |
| :-- | --: |
|  | command: login, nick: foobar |
| _error: 1001_ |  |
| player_id: 6 |  |
| games: [{id: 1, players: [Foo, Bar, Joe]}, {id: 2, players: [Too, True, Mrazek]}] | |
|  | command: select, game_id: 2 |
| _error: 1002_ | |

### Pre-start stage
| to client from server | to server from client |
| :-- | --: |
| **command: player\_ready, player\_id: 3** | |
| **command: player\_add, p\_id: 3, g\_id: 2, p\_color: #abcdef** | |
| command: start, time: 10 | |
| set: planet, values: {id: 1, x: 1024, y: 512, owner_id: 6} ||




### error codes & messages
| error code | error message |
| --- | --- |
| 1001 | nick has been already used |
| 1002 | this game has been already started |
