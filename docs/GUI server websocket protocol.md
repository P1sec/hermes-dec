# GUI Websocket protocol

The browser/Websocket-based GUI of `hermes-dec` should implement the following JSON messages:

```
S->C {"type": "recent_files", recent_files: [
    {
        "file_hash": ...,
        "orig_name": ...
    }, ...
]} (saved files w/ context, etc.)

C->S {"type": "open_file_by_hash", "file_hash": "<sha256 HEX>"} (load saved context)

S->C {"type": "file_hash_unknown"}

// (Implement first:)
C->S {"type": "begin_tranfer", "file_name": "x.index.bundle OR apk"}
(Raw binary buffer websocket transmission...)
C->S {"type": "end_transfer"}

// (Maybe implement later): We should both prompt the user using our own file shell (in order to have the full path) and copy the file name + metadata + size + origin path + create a parameters file in ~/.hermes-dec:
C->S {"type": "open_file", "disk_path": "(...)/x.index.bundle"}

S->C {"type": "pop_message", "icon": "error", "message_html": "Could not open file:<br><br><pre>XXX</pre>"}

S->C {
    "type": "file_opened",
    "file_metadata": {
        "bytecode_version": 76,
        "db_created_time": "2023-04-07T08:33:57.200578",
        "db_updated_time": "2023-07-18T13:53:13.827344",
        "dir_disk_path": "/home/marin/.local/share/HermesDec/by-date/2023-04-07T08:33:56-indexandroidbundle",
        "file_hash": "b2b514abac3dedbc83619d0e782ae61a0d958038a432f01a11b22d09537d7090",
        "file_size": 3482132,
        "orig_name": "index.android.bundle",
        "raw_disk_path": "/home/marin/.local/share/HermesDec/by-date/2023-04-07T08:33:56-indexandroidbundle/index.android.bundle"
    },
    "functions_list": [{"name": "fun_000001", "offset": '%08x' % 0x40234, size: 42}, ...]
}
// The "functions_list" attribute in the corresponding JSON object should be indexable
// the same way as in the Hermes bytecode file format.

C->S {"type": "analyze_function", "function_id": 49}
// Will return disassembly graph + cross-references + decompiled code with clickable expandable "..." buttons for nested closures for a given function

S->C {"type": "analyzed_function", "function_id": 49, "blocks": [{
    "grid_x": 1, // Used for rendering with the CSS grid layout
    "grid_y": 2,
    "text": "Assembly...\n",
    "child_nodes": [index, index...],
    "child_error_nodes": [index, index...],
    "parent_nodes": [index, index...],
    "parent_error_nodes": [index, index...]
}]}

(+ a progress bar upstream packet?)

(+ a search feature?)

(+ a code export button?)
```