const open_button = document.querySelector('#open_button');
const file_picker = document.querySelector('#file_picker');

open_button.onclick = function() {
    file_picker.click();
};

file_picker.onchange = function(event) {
    console.log('DEBUG: File picker result: => ', event);

    if(event.target.files.length) {
        let file = event.target.files[0];

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
    }
};
