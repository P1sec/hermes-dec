/**
 * TODO: Write an APK extractor on the server later...
 * 
 */

OTODODO
TRASH THIS

const open_button = document.querySelector('#open_button');
const file_picker = document.querySelector('#file_picker');

open_button.onclick = function() {
    file_picker.click();
};

file_picker.onchange = function(event) {
    console.log('DEBUG: File picker result: => ', event);

    if(event.target.files.length) {
        let file = event.target.files[0];

        window.current_file_obj = file;

        file.arrayBuffer().then(function(array_buffer) {
            hash_file_buffer(array_buffer).then(function(file_hash) {

                window.socket.send(JSON.stringify({
                    type: 'open_file_by_hash',
                    hash: file_hash
                }));

                window.hash_router.current_file_sha = file_hash;
                window.hash_router.data.file_hash = file_hash;
                window.hash_router.update();

            });
        });
    }
};
