window.socket = new WebSocket('ws://localhost:49594');
window.current_file_obj = null;

const functions_table = document.querySelector('#functions_table tbody');
const home_view = document.querySelector('#home_view');
const work_view = document.querySelector('#work_view');

const select_function = function(function_id) {

    window.socket.send(JSON.stringify({
        type: 'analyze_function',
        function_id: function_id
    }));

    window.hash_router.current_function_id = function_id;
    window.hash_router.data.current_function = function_id;
    window.hash_router.update();

    // WIP ..
};

const format_size = function(size) { // Format a size in MiB or KiB
    if(size >= 1024 * 1024) { // More than 1 MiB?
        return Math.floor(size / 1024 / 1024 * 10) / 10 + ' MiB';
    }
    else {
        return Math.floor(size / 1024 / 1024 * 10) / 10 + ' KiB';
    }
};

const format_date = function(date) {
    return date; // WIP
};

window.socket.onopen = function() {
    window.hash_router = new HashRouter();
}

window.socket.onmessage = function(event) {
    let message = JSON.parse(event.data);

    console.log('DEBUG: Received:', message);

    // Please see the "../../../docs/GUI server websocket protocol.md"
    // file for documentation about the following messages.

    switch(message.type) {
        case 'recent_files':
            const tbody = document.querySelector('#recent_files_table tbody');

            if(message.recent_files.length) {
                document.querySelector('#recent_files_table').style.display = 'table';
            }

            for(let recent_file of message.recent_files) {
                const tr = document.createElement('tr');

                const items = [
                    recent_file.orig_name,
                    format_size(recent_file.file_size),
                    recent_file.file_hash.substr(0, 7),
                    format_date(recent_file.db_created_time),
                    format_date(recent_file.db_updated_time)
                ];

                for(var data_item of items) {
                    const td = document.createElement('td');
                    td.textContent = data_item;
                    tr.appendChild(td);
                }

                tr.addEventListener('click', function(event) {
                    window.socket.send(JSON.stringify({
                        type: 'open_file_by_hash',
                        hash: recent_file.file_hash
                    }), true);

                    window.hash_router.current_file_sha = recent_file.file_hash;
                    window.hash_router.data.file_hash = recent_file.file_hash;
                    window.hash_router.update();
                });

                tbody.appendChild(tr);

            }

            break; // WIP - TODO

        case 'file_hash_unknown':
            let file = window.current_file_obj;

            window.socket.send(JSON.stringify({
                type: 'begin_transfer',
                file_name: file.name
            }));

            let chunk_size = 1 * 1024 * 1024;
            for(let pos = 0; pos < file.size; pos += chunk_size) {
                window.socket.send(file.slice(pos, Math.min(file.size, pos + chunk_size)));
            }

            window.socket.send(JSON.stringify({
                type: 'end_transfer'
            }));
            break;

        case 'file_opened':
            window.hash_router.file_opened = true;
            window.hash_router.parse_hash(); // Analyze a function from the URL hash, if specified

            home_view.style.display = 'none';
            work_view.style.display = 'flex';

            for(let function_id = 0; function_id < message.functions_list.length; function_id++) {
                let function_obj = message.functions_list[function_id];

                let row = document.createElement('tr');

                let cell = document.createElement('td');
                cell.textContent = function_obj.name;
                row.appendChild(cell);

                cell = document.createElement('td');
                cell.textContent = function_obj.offset;
                row.appendChild(cell);

                cell = document.createElement('td');
                cell.textContent = function_obj.size;
                row.appendChild(cell);

                row.addEventListener('click', function(event) {
                    let function_id = Array.prototype.indexOf.call(event.currentTarget.parentNode.children, event.currentTarget);

                    select_function(function_id);
                }, true);

                functions_table.appendChild(row);
            }
            break;
        
        case 'analyzed_function':

            const canvas_grid = document.querySelector('#canvas_grid');
            canvas_grid.innerHTML = '';

            const TILE_SIZE_Y = 12;
            const TILE_SIZE_X = 12;

            const svg_tag = document.querySelector('#canvas_svg');
            svg_tag.innerHTML = '';

            let graph = new Graph(svg_tag, canvas_grid);
            let node_objects = [];

            for(var block_idx = 0; block_idx < message.blocks.length; block_idx++) {
                var block = message.blocks[block_idx];

                var html_block = document.createElement('div');

                // We're using a 1-indexed CSS grid layout.
                // When both indexes are even it's a node,
                // when either index (row or column) is odd it's a lattice
                html_block.style.gridColumn = block.grid_x * 2;
                html_block.style.gridRow = block.grid_y * 2;
                
                var node_div = document.createElement('div');
                node_div.className = 'graph_node';
                node_div.textContent = block.text;
                html_block.appendChild(node_div);

                var node = new Node(graph, html_block, block_idx);
                node_objects.push(node);

                canvas_grid.appendChild(html_block);
            }

            for(var block_idx = 0; block_idx < message.blocks.length; block_idx++) {
                var block = message.blocks[block_idx];
                var node = node_objects[block_idx];

                for(var child_port_idx of block.child_nodes) {
                    var out_port = new OutPort(graph, node, false);
                    var in_port = new InPort(graph, node_objects[child_port_idx], false);
                    new Edge(graph, out_port, in_port);
                }
                for(var child_port_idx of block.child_error_nodes) {
                    var out_port = new OutPort(graph, node, true);
                    var in_port = new InPort(graph, node_objects[child_port_idx], true);
                    new Edge(graph, out_port, in_port);
                }
            }

            graph.prerender();
            graph.render();

            break;

            // WIP fix display introduce graph ordering introduce links pathfinding ...
    
    }
};

window.socket.onclose = function() {
    document.body.innerHTML = '<h1>Socket closed<h1>'; // Temporary?
    // Put something here/handle ping time-outs etc.
};