var FilePicker = {
    emits: [
        'upload_file'
    ],
    
    methods: {
        pick_file(event) {
            console.log('DEBUG: File picker result: => ', event);

            if(event.target.files.length) {
                let file = event.target.files[0];
        
                let self = this;
                file.arrayBuffer().then(function(array_buffer) {
                    hash_file_buffer(array_buffer).then(function(file_hash) {

                        self.$emit('upload_file', file, file_hash);
        
                    });
                });
            }
        },

        trigger_click() {
            this.$refs.file_picker.click();
        }
    },

    template: `<div id="open_button_container">
        <label>
            <span style="margin-right: 5px">➡️</span> Analyze a new file:
            <input type="button" id="open_button" @click="trigger_click" value="Open a file...">
        </label>
        <input type="file" ref="file_picker"
            id="file_picker" accept=".bundle, .hbc, .apk"
            @change="pick_file"
            style="display: none">
    </div>`
};