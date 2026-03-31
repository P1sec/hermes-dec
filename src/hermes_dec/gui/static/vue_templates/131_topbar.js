var TopBar = {
    props: {
        file_metadata: Object
    },

    emits: ['switch_file'],

    methods: {
        format_date(date) {
            return format_date(date);
        },
        format_size(size) {
            return format_size(size);
        }
    },

    template: `<div id="top_bar">
        <span id="top_bar_label">
            "{{ file_metadata.orig_name }}" |
            Opened {{ format_date(file_metadata.db_created_time) }} |
            Hermes bytecode v{{ file_metadata.bytecode_version }} |
            {{ format_size(file_metadata.file_size) }}
        </span>
        <input id="top_bar_switch_file_button" type="button"
            value="Switch file" @click="$emit('switch_file')">
    </div>`
};