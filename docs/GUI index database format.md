# GUI index database format

This file summarizes and describes the data that should be indexed in order to speed up/allow for checking cross-refernces/dumping decompiled code over the `hermes-dec` GUI.

## Summary of use/dataset pairs

XX

In order to *implement viewing cross-references for function cross-references (both from the side pane of the application and the decompiled code) of the `hermes-dec` web UI*, we should implement the following functionality:
- XX

In order to *implement viewing cross-references for raw strings in the HBC file(both from the side pane of the application and the decompiled code) of the `hermes-dec` web UI*, we should implement the following functionality:
- XX

In order to *implement searching for function names and offsets from the left side pane of the `hermes-dec` web UI*, we should implement the following functionality:
- XX

In order to *implement searching for raw strings in the HBC file from the left side pane of the `hermes-dec` web UI*, we should implement the following functionality:
- XX

In order to *implement viewing decompiled code with cross-references in the code browser of the `hermes-dec` web UI*, we should implement the following functionality:
- XX


## Cross-reference database

### Code common to launching the indexer subprocess

- In `server.py` entry point -> `WebsocketServer.handle_ws_client`
  - `server.py` -> `WebsocketClient.create_file`
    - `project_meta.py` -> `ProjectInstanceManager.new_with_name`
      - `self.subdir_path` = `join(user_data_dir('HermesDec', 'P1Security'), self.gen_unique_dirname(name))`
        - Creates: `self.subdir_path` = `/home/marin/.local/share/HermesDec/by-date/2023-09-06T20:53:55-samplehbc/' + '{index.android.bundle,metadata.json}`
  - `server.py` -> `WebsocketClient.parse_file`
    - `project_meta.py` -> `ProjectInstanceManager.save_to_disk`
      - `project_meta.py` -> `ProjectInstanceManager.write_or_update_metadata` (writes `metadata.json` in the project directory)
    - `ProjectInstanceManager.write_or_update_metadata` also called here for updating the bytecode version
  - `server.py` -> `WebsocketClient.spawn_indexer`
    - (xxx: code to write with ensure_future(asyncio.spawn_subprocess XX) + launching subprocess as described in the GUI index worker pipe IPC.md" file + watching the output and doing communication with the Websocket and local object state when needed)

### Functions/function and function/built-in cross-references (SQLite DB)

The application should maintain, in an SQLite database, a repository of cross-refences between HBC functions and the string IDs, function IDs, and built-in IDs they reference.

This information should be referenced into the SQLite/SQLAlchemy defined in "`src/gui/index_worker/index_db.py`".

In order to perform clean paralellization and to avoid daemon thread-related or GIL-related issues, indexing should be done into a subprocess that frequently reports its state of indexing through a `stdout`-based pipe mechanism, along with other indexing tasks described in the present document, as described in the `GUI index worker pipe IPC.md` document present in the current directory.

XX Implementation notes
XX

Call chain:




### Function strings cross-references (SQLite DB)

XX

## Functions list (free-text search/SQLite DB?)

XX

## Strings list (free-text search/SQLite DB?)

XX

## Pre-generated decompiled code with inline x-refs (SQLite DB/custom markup?)

XX
