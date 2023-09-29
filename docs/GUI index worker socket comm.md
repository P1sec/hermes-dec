This document presents the local UDP socket-based communication used for the decompiler/index worker to communicate with the main Websocket server worker over the `hermes-dec` GUI [ TODO: Make it one-simplex per thread socket in the subprocess, with passing the data directory as an argument to the subprocess, with a secondary thread listening to pings? b.c watching for PIDs is too single-platform? ].

In the reference below, `S` denotes the main/Websocket server worker, and the `C` denotes the decompiler/index worker.

Communication is done over a local UDP socket which random unused listening ports picked (one for both sides of the socket) between 40000 and 59999, which is stored in a JSON file located at "$(tempfile.gettempdir())/hermes_dec_runfile.json". The JSON syntax of the latter file is also listen below.

The local socket also exchanges a ping message at most every minute with a time-out of 40 secondes in order to ensure that the other side of the socket is still alive. If not, the main/Websocket worker displays a message of the GUI user, of the decompiler/index worker closes as soon as no significant database operation is more ingoing (with possibly a canary thread in each process looking for frozedness/a zombie decompiler/index work process being killed by the parent main/websocket worker process at the launch of a new server/any other useful mechanisms useful for preserving the process list running for the application over the host system in a clean state).

## `hermes_dec_runfile.json` contents

TODO XXX
This file is used as an exclusive lock for the `hermes-dec` main server process appliance.

It should contain the PID for the running main/Websocket server worker process (it also acts as a lockfile, as only one may be running over the host system) and the UDP ports for both sides of the socket.

Sample contents:

```json
{
    "main_worker_pid": 199,
    "main_worker_port": 49594,
    "index_workers": [
        {
            "pid": 939,
            "port": 9099
        }    
    ]
}
```

## UDP socket communication spec

The following message types shall be implemented:

- `ping` (`S->C` or `C->S`): sent at most every minute as a keep-alive for the implicit UDP connection (see the information in the introductory part of this file for implementation notes/suggestions.)   (<-- Has given thread in subprocess for receiving/sending)
Example: ```json
{
    "type": "ping"
}```

- `pong` (`C->S` or `S->C`): a response to the `ping` message
Example: ```json
{
    "type": "pong"
}```

- `open_file` (`C->S`): transmit disk paths indicating a local data folder and a full bundle file path for the current `hermes-dec` project, in order to launch the indexing process or to load the index in the case where it was already generated  (<<<<<--- TODO: RM This: Rather use a subprocess?)
Example: ```json
{
    "type": "open_file",
    "data_folder_path": "",
    "raw_file_path": ""
}
```

- `indexing_state` (`S->C`): inform the Websocket worker process about the state of the indexing (immediatly after he index has been loaded from disk if it was alreay generated earlier, or at every step of the data generation process) along with an estimated process rate ranging from 0 to 100 when finished
Example: ```json
{
    "type": "indexing_state",
    "state": "began_indexing" | "indexing_strings" | "indexing_functions" | "decompiling_code" | "fully_indexed" | "XXX"
    "process_percent": 95
}
```

- `indexing_status_log` (`S->C`): transmit a readable log string about the indexing status of the document
Example: ``json
XXX
```

- ``

## Fetching the indexed and text chunk-decompiled data

Fetching the indexed and text chunk-decompiled data is done in the process of the main worker, thanks to the shared SQLAlchemy ORM code with the main process. (Once all the code has been decompiled, the secondary/index worker emits its status and closes)

## TODO also

Check whether the pass1b/1c of the decompilation pipeline are still required when just decompiling and not rendering the UI graph.

(Also obviously send their text status comments regularly to the new decompilation pipeline processing console at the bottom pane of the web UI in order to be able to debug where the background decompilation process takes times, freezes, crashes, etc.)

### ---> TOOD ALL FIRST MAYBE ?

Attempt to produce minial debugging output/time measurement over the decompilation process, in order to find out especially which subroutines get stuck out over pass 1c when the full decompilation process includes pass 1c in our test HBC bundle, and why?