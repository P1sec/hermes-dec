window.socket = new WebSocket('ws://localhost:49594');
window.current_file_obj = null;

const functions_table = document.querySelector('#functions_table tbody');
const home_view = document.querySelector('#home_view');
const work_view = document.querySelector('#work_view');

const select_function = function(event) {
    let function_id = Array.prototype.indexOf.call(event.currentTarget.parentNode.children, event.currentTarget);

    window.socket.send(JSON.stringify({
        type: 'analyze_function',
        function_id: function_id
    }));

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

                row.addEventListener('click', select_function, true);

                functions_table.appendChild(row);
            }
            break;
        
        case 'analyzed_function':

            const canvas = document.querySelector('#canvas');
            canvas.innerHTML = '';

            const TILE_SIZE_Y = 12;
            const TILE_SIZE_X = 12;

            for(var block of message.blocks) {
                var html_block = document.createElement('div');
                html_block.style.gridColumn = block.grid_x;
                html_block.style.gridRow = block.grid_y;
                
                var node_div = document.createElement('div');
                node_div.className = 'graph_node';
                node_div.textContent = block.text;
                html_block.appendChild(node_div);

                canvas.appendChild(html_block);
            }
            break;

            // WIP fix display introduce graph ordering introduce links pathfinding ...
    
    }
};

window.socket.onclose = function() {
    document.body.innerHTML = '<h1>Socket closed<h1>'; // Temporary?
    // Put something here/handle ping time-outs etc.
};