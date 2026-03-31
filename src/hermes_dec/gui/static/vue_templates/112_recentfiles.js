var RecentFiles = {
    emits: [
        'open_hash'
    ],

    props: {
        recent_files: Array
    },
    
    methods: {
        format_date(data) {
            return format_date(data);
        },
        format_size(data) {
            return format_size(data);
        }
    },

    template: `<h1>Recently opened files</h1>
        <br>
        <table id="recent_files_table">
            <thead>
                <tr>
                    <th>File name</th>
                    <th>File size</th>
                    <th>File hash</th>
                    <th>Uploaded date</th>
                    <th>Modified date</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="recent_file of recent_files"
                    @click="$emit('open_hash', recent_file.file_hash)">
                    <td>{{ recent_file.orig_name }}</td>
                    <td>{{ format_size(recent_file.file_size) }}</td>
                    <td>{{ recent_file.file_hash.substr(0, 7) }}</td>
                    <td>{{ format_date(recent_file.db_created_time) }}</td>
                    <td>{{ format_date(recent_file.db_updated_time) }}</td>
                </tr>
            </tbody>
        </table>`
};