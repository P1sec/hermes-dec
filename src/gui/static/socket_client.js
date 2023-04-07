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

window.socket.onmessage = function(event) {
    let message = JSON.parse(event.data);

    console.log('DEBUG: Received:', message);

    // Please see the "../../../docs/GUI server websocket protocol.md"
    // file for documentation about the following messages.

    switch(message.type) {
        case 'recent_files':
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
                html_block.className = 'graph_node';
                html_block.style.top = block.y * TILE_SIZE_Y + 'px';
                html_block.style.left = block.x * TILE_SIZE_X + 'px';
                html_block.style.width = block.width * TILE_SIZE_X + 'px';
                html_block.style.height = block.height * TILE_SIZE_Y + 'px';
                html_block.textContent = block.raw_text;

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