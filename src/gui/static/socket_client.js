window.socket = new WebSocket('ws://localhost:49594');

const functions_table = document.querySelector('#functions_table tbody');
const home_view = document.querySelector('#home_view');
const work_view = document.querySelector('#work_view');

const select_function = function(event) {
    let function_id = Array.prototype.indexOf.call(event.target.parentNode.children, event.target);

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
    
    }
};

window.socket.onclose = function() {
    document.body.innerHTML = '<h1>Socket closed<h1>'; // Temporary?
    // Put something here/handle ping time-outs etc.
};