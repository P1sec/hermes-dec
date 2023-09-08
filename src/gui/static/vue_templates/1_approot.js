// WIP..
var AppRoot = {
    data() {
        return {
            // Websocket connection handling:
            socket: null, // The websocket object to be created itself
            is_connected: false, // Reactive state for syncing with the Websocket state
            is_retrying: false,
            parsed_url_initially: false,
            current_file_obj: null,

            // URL router handling (be sure to set all defaults to "null"):
            hash_data: { // URL hash JSON data as currently present in the page's URL
                file_hash: null, // SHA-256 lowercase hex string if set
                current_function: null,

                current_tab: null, // Not listed in sync_data
                    // ^ Enum string, any of: "disasm_view" (default),
                    //   "string_view", "decompile_view"
                    // (see "133_tabview.js" for the full definition)
            },
            sync_data: { // URL hash JSON data as it matches the content effectively
                // retrieved from the WebSocket's URL
                file_hash: null,
                current_function: null,
                
            },

            // Data to be downloaded from the upstream:
            dl: {
                current_message: null, // (Any view, popover - Retrieved from the "pop_message" wire message)
                current_message_icon: null, // (same)

                recent_files: null, // (Home view) (Retrieved from the "recent_files" wire message)

                file_metadata: null, // (Main view > Top bar) (Retrieved from the "file_opened" wire message)
                functions_list: null, // (Main view > Sidebar) (Retrieved from the "file_opened" wire message - TODO paginate this w/ scroll event handler?)

                disasm_blocks: null, // (Main view > Body > Disasm tab) (Retrieved from the "analyzed_function" wire message),

                strings_list: null // (Main view > Body > Strings tab) (to be implemented/considered - TODO paginate this?)
            }
        }
    },

    components: {
        HomeView,
        LoadView,
        WorkView
    },

    watch: {
        hash_data: {
            handler(new_value, same_value) {
                if(!this.parsed_url_initially) {
                    return;
                }

                var fields = [];
                for(var field in this.hash_data) {
                    if(field && this.hash_data[field] != null) {
                        fields.push(field + '=' + this.hash_data[field]);
                    }
                }

                var replacement_str = fields.join('/');
                var current_str = decodeURIComponent(location.hash.slice(1));

                if(replacement_str !== current_str) {
                    location.hash = '#' + replacement_str;
                }
            },
            deep: true
        }
    },

    methods: {
        open_socket() {
            this.socket = new WebSocket('ws://localhost:49594');

            this.socket.onopen = this.socket_open.bind(this);
            this.socket.onmessage = this.socket_message.bind(this);
            this.socket.onclose = this.socket_closed.bind(this);    
        },
        socket_open() {
            this.is_connected = true;
            this.is_retrying = false;
        },
        socket_message(event) {
            console.log('DEBUG: WS received: ' + event.data);
            var message = JSON.parse(event.data);
            
            switch(message.type) {
                case 'recent_files':
                    this.dl.recent_files = message.recent_files;
                    break;
                
                case 'file_hash_unknown':
                    var file = this.current_file_obj;

                    this.socket.send(JSON.stringify({
                        type: 'begin_transfer',
                        file_name: file.name
                    }));

                    var chunk_size = 1 * 1024 * 1024;
                    for(var pos = 0; pos < file.size; pos += chunk_size) {
                        this.socket.send(file.slice(pos, Math.min(file.size, pos + chunk_size)));
                    }

                    this.socket.send(JSON.stringify({
                        type: 'end_transfer'
                    }));
                    break;
                
                case 'file_opened':
                    this.sync_data.file_hash = message.file_metadata.file_hash;

                    this.dl.file_metadata = message.file_metadata;
                    this.dl.functions_list = message.functions_list;

                    this.hash_data.current_function = this.hash_data.current_function || 0;
                    this.hash_data.current_tab = this.hash_data.current_tab || 'disasm_view';
                    break;
                
                case 'analyzed_function':
                    this.sync_data.current_function = message.function_id;
                    this.dl.disasm_blocks = message.blocks;

                    break;
            }
        },
        socket_closed() {
            this.is_connected = false;
            this.is_retrying = true;

            for(var key in this.dl) {
                this.dl[key] = null;
            }
            for(var key in this.sync_data) {
                this.sync_data[key] = null;
            }

            const RETRY_DELAY = 5000;
            window.setTimeout(function(self) {
                self.open_socket();
            }, RETRY_DELAY, this);
        },

        sync_hash_from_url() {
            var new_data = {};
            for(var field of location.hash.slice(1).split('/')) {
                var split_field = field.split('=');
                if(split_field.length == 2) {
                    new_data[split_field[0]] = split_field[1];
                }
            }
            for(var prop in new_data) {
                if(new_data[prop] != this.hash_data[prop]) {
                    Object.assign(this.hash_data, new_data);
                    break;
                }
            }
            this.parsed_url_initially = true;
        },

        set_current_tab(tab_name) {
            this.hash_data.current_tab = tab_name;
        },

        select_function(function_id) {
            if(this.hash_data.current_function != function_id) {
                this.hash_data.current_function = function_id;
            }
        },
        select_function_command() {
            if(this.hash_data.current_function != this.sync_data.current_function) {
                this.socket.send(JSON.stringify({
                    type: 'analyze_function',
                    function_id: parseInt(this.hash_data.current_function, 10)
                }));
            }
        },

        switch_file() {
            for(var key in this.dl) {
                if(key !== 'recent_files') {
                    this.dl[key] = null;
                }
            }
            for(var key in this.sync_data) {
                this.sync_data[key] = null;
            }
            for(var key in this.hash_data) {
                if(this.hash_data[key] != null) {
                    this.hash_data[key] = null;
                }
            }
        },

        upload_file(file, file_hash) {
            this.current_file_obj = file;
            this.open_hash(file_hash);
        },
        open_hash(file_hash) {
            this.hash_data.file_hash = file_hash;
        },
        open_hash_command() {
            this.socket.send(JSON.stringify({
                type: 'open_file_by_hash',
                hash: this.hash_data.file_hash
            }));
        }
    },

    created() {
        window.onhashchange = this.sync_hash_from_url.bind(this);
        this.sync_hash_from_url();

        this.open_socket();
    },

    template: `<template v-if="!is_connected || !dl.recent_files">
        <template v-if="!is_retrying">
            <h1>Connecting to socket...</h1>
        </template>
        <template v-else>
            <h1>Trying to reconnect to socket...</h1>
        </template>
    </template>
    <template v-else>
        <template v-if="hash_data.file_hash != sync_data.file_hash">
            <LoadView @open_hash_command="open_hash_command" />
        </template>
        <template v-else-if="!dl.file_metadata">
            <HomeView :recent_files="dl.recent_files"
                @upload_file="upload_file" @open_hash="open_hash" />
        </template>
        <template v-else>
            <WorkView
                :file_metadata="dl.file_metadata"
                :current_function="hash_data.current_function"
                :function_is_syncing="hash_data.current_function != sync_data.current_function"
                :current_tab="hash_data.current_tab"
                :functions_list="dl.functions_list"
                :disasm_blocks="dl.disasm_blocks"
                @switch_file="switch_file"
                @select_function="select_function"
                @select_function_command="select_function_command"
                @set_current_tab="set_current_tab" />
            <!-- TODO.. -->
        </template>
    </template>`
    // template: (WIP.)
    //     <template v-if="is_connected"> etc.
};