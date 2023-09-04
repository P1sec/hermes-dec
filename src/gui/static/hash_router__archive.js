// WIP..

/**
 * TODO (2023-04-06):
 * 
 * First, ensure that we correctly copy data onto the disk
 * into "project_meta.py" so that we can reuse it later
 *  a) Display a list of the data in "~/.local/share/HermesDec/"
 *     so that it can be deleted/we do not reupload too much the
 *     same thing (also maybe SHA-256 hash-name files/directory?)
 * 
 * Then, store raw JSON data in the URL hash, in the form of:
 * {
 *     "file_hash": "<SHA256>",
 *     "current_function": null, // or Integer
 *     "current_tab": null, // or Enum string, any of: "disasm_view", "string_view", "decompile_view"
 *     // WIP ...
 * }
 * 
 * Then, read this data on page load correctly so that we can
 * test our changes quickly later
 */data.

// TOOD
/DIDNO
NOT£

HTMLTimeElementDs!s!s




// The object below is instancied once the WebSocket connection
// has been established (in "socket_client.js"), so that
// interactivity of the interface can be guaranteed.
//
// It is then stored in the "window.hash_router" variable.

class HashRouter {
    constructor() {
        this.current_file_sha = null;
        this.current_function_id = null;
        this.current_tab = null;
        this.file_opened = false;
        this.data = {};
        this.parse_hash();

        window.onhashchange = this.parse_hash.bind(this);
    }

    parse_hash() {
        try {
            this.data = JSON.parse(decodeURIComponent(location.hash.slice(1)));
        }
        catch(e) { }

        if(this.data.file_hash && this.current_file_sha !== this.data.file_hash) {
            this.current_file_sha = this.data.file_hash;
            window.socket.send(JSON.stringify({
                type: 'open_file_by_hash',
                hash: this.current_file_sha
            }));
        }

        if(this.file_opened && this.data.current_function && this.current_function_id !== this.data.current_function) {
            this.current_function_id = this.data.current_function;

            window.socket.send(JSON.stringify({
                type: 'analyze_function',
                function_id: this.current_function_id
            }));
         }
    }

    update() {
        location.hash = '#' + encodeURIComponent(JSON.stringify(this.data));
    }
}