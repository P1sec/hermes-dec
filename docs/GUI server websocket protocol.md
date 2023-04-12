# GUI Websocket protocol

The browser/Websocket-based GUI of `hermes-dec` should implement the following JSON messages:

```
S->C {"type": "recent_files", ...} (saved files w/ context, etc.)

C->S {"type": "open_file_by_hash", "file_hash": "<sha256 HEX>"} (load saved context)

S->C {"type": "file_hash_unknown"}

// (Implement first:)
C->S {"type": "begin_tranfer", "file_name": "x.index.bundle OR apk"}
(Raw binary buffer websocket transmission...)
C->S {"type": "end_transfer"}

// (Maybe implement later): We should both prompt the user using our own file shell (in order to have the full path) and copy the file name + metadata + size + origin path + create a parameters file in ~/.hermes-dec:
C->S {"type": "open_file", "disk_path": "(...)/x.index.bundle"}

S->C {"type": "pop_message", "icon": "error", "message_html": "Could not open file:<br><br><pre>XXX</pre>"}

S->C {"type": "file_opened", "functions_list": [{"name": "fun_000001", "offset": '%08x' % 0x40234, size: 42}, ...]}
// The "functions_list" attribute in the corresponding JSON object should be indexable
// the same way as in the Hermes bytecode file format.

C->S {"type": "analyze_function", "function_id": 49}
// Will return disassembly graph + cross-references + decompiled code with clickable expandable "..." buttons for nested closures for a given function

S->C {"type": "analyzed_function", "function_id": 49, "blocks": [{
    "grid_x": 1, // Used for rendering with the CSS grid layout
    "grid_y": 2,
    "text": "Assembly...\n",
    "WIP... // Links"
}],
"edges": ["WIP..."]}

(+ a progress bar upstream packet?)

(+ a search feature?)

(+ a code export button?)
```