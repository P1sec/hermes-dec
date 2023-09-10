var WorkView = {
    props: {
        file_metadata: Object,
        functions_list: Array,
        header_info: Array,
        current_function: Number,
        function_is_syncing: Boolean,
        current_tab: String,
        disasm_blocks: Object
    },

    emits: [
        'switch_file',
        'select_function',
        'select_function_command',
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
            :functions_list="functions_list"
            :header_info="header_info"
            @select_function="select_function" />
        <template v-if="function_is_syncing">
            <h1 style="margin-left: 26px">Loading function data...</h1>
        </template>
        <template v-else-if="current_function != null">
            <MainPane
                :current_function="current_function"
                :current_tab="current_tab"
                :disasm_blocks="disasm_blocks"
                @set_current_tab="set_current_tab" />
        </template>
    </div>`
};