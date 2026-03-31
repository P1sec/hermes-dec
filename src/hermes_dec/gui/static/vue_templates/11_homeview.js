var HomeView = {
    props: {
        recent_files: Array
    },

    emits: [
        'open_hash',
        'upload_file'
    ],

    methods: {
        open_hash(file_hash) {
            this.$emit('open_hash', file_hash);
        },

        upload_file(file, file_hash) {
            this.$emit('upload_file', file, file_hash);
        }
    },

    components: {
        FilePicker,
        RecentFiles
    },

    // File open/recently opened options
    template: `<div id="home_view">
    <FilePicker @upload_file="upload_file" />
    <template v-if="recent_files.length">
        <br>
        <RecentFiles :recent_files="recent_files"
            @open_hash="open_hash" />
    </template>
</div>`
};