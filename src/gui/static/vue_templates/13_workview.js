var WorkView = {
    props: {
        file_metadata: Object,
        current_tab: String,
        functions_list: Array
    },

    emits: [
        'switch_file',
        'set_current_tab',
        'select_function'
    ],

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
        FunctionsList,
        TabView
    },

    template: `<div id="work_view">
        <TopBar
            :file_metadata="file_metadata"
            @switch_file="$emit('switch_file')" />
        <FunctionsList
            :functions_list="functions_list"
            @select_function="select_function" />
        <TabView
            :current_tab="current_tab"
            @set_current_tab="set_current_tab" />
    </div>`
};