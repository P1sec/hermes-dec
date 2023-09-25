var WorkView = {
    props: {
        file_metadata: Object,
        table_data_map: Object,
        current_function: Number,
        function_is_syncing: Boolean,
        current_tab: String,
        disasm_blocks: Object
    },

    emits: [
        'switch_file',
        'select_function',
        'select_function_command',
        'load_table',
        'set_current_tab'
    ],

    watch: {
        current_function: {
            handler(new_value) {
                this.$emit('select_function_command');
            },
            immediate: true
        }
    },

    methods: {
        load_table(...args) {
            this.$emit('load_table', ...args);
        },

        select_function(function_id) {
            this.$emit('select_function', function_id);
        },

        set_current_tab(tab_name) {
            this.$emit('set_current_tab', tab_name);
        }
    },

    components: {
        TopBar,
        SidePane,
        MainPane
    },

    template: `<div id="work_view">
        <TopBar
            :file_metadata="file_metadata"
            @switch_file="$emit('switch_file')" />
        <SidePane
            :current_function="current_function"
            :table_data_map="table_data_map"
            @load_table="load_table"
            @select_function="select_function" />
        <template v-if="current_function != null">
            <MainPane
                :current_function="current_function"
                :current_tab="current_tab"
                :function_is_syncing="function_is_syncing"
                :disasm_blocks="disasm_blocks"
                @set_current_tab="set_current_tab" />
        </template>
    </div>`
};