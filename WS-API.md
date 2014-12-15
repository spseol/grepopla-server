# WS API Overview

_optional_ - **for both directions** 

### Pre-game stage
| to client from server | to server from client |
| :-- | --: |
|  | command: login, nick: foobar |
| _error: 1001_ |  |
| player_id: 6 |  |
| games: [{id: 1, players: [Foo,Bar,Joe]}, {id: 2, players: [Too, True, Mrazek]}] | |
|  | command: select, game_id: 2 |

### Pre-start stage
| to client from server | to server from client |
| :-- | --: |
| command: player_add, player_id: 3 |




### error codes & messages
| error code | error message |
| --- | --- |
| 1001 | nick foobar has been already used |
