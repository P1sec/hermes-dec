This document presents the interprocess communication used for the decompiler/index worker to communicate with the main Websocket server worker over the `hermes-dec` GUI.

Communication is done over unidirectional unbuffered process pipe (stdout) communication, and passing CLI arguments + UNIX signal for cancelling on the other side.

## Subprocess args

The subprocess shall have the following arguments:

```
argv[0]: Python interpreter
argv[1]: Worker script full path
argv[2]: Data folder path
argv[3]: Raw .HBC file path
```

## Cancel signal (parent->child)

Just a SIGINT/simulated CTRL+C should be used for ending out the subprocess when needed (for example when the parent process gets interrupted itself)

We should maybe simulate `prctl(PR_SET_PDEATHSIG` on Linux (in addition to our `atexit` call) to do this cleanly.

## Child end signal (child->parent)

The subprocess should terminate when the whole document has been indexed (or was already indexed and the indexing data can be loaded immediately).

## Line-delimited JSON subprocess pipe communication spec (child->parent)

The following message types shall be implemented, and serialized with a `\n` endline through stdout:

- `indexing_state`: inform the Websocket worker process about the state of the indexing (immediately after he index has been loaded from disk if it was alreay generated earlier, or at every step of the data generation process) along with an estimated process rate ranging from 0 to 100 when finished
Example: ```json
{
    "type": "indexing_state",
    "state": "began_indexing" | "indexing_strings" | "indexing_functions" | "decompiling_code" | "fully_indexed" | "XXX",
    "process_percent": 95
}
```

- `indexing_status_log`: transmit a readable log string about the indexing status of the document
Example: ``json
{
    "type": "indexing_status_log",
    "message": "Text line to log"
}
```

- ``

## Fetching the indexed and text chunk-decompiled data

Fetching the indexed and text chunk-decompiled data is done in the process of the main worker, thanks to the shared SQLAlchemy ORM code with the main process. (Once all the code has been decompiled, the secondary/index worker emits its status and closes)

## TODO also

Check whether the pass1b/1c of the decompilation pipeline are still required when just decompiling and not rendering the UI graph. (=> Yes, it will be used to optionally reconstruct contron flow later)

(Also obviously send their text status comments regularly to the new decompilation pipeline processing console at the bottom pane of the web UI in order to be able to debug where the background decompilation process takes times, freezes, crashes, etc.)