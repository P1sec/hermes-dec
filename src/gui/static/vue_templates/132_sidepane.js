var SidePane = {
    data() {
        return {
            current_tab: 'functions_list',

            // Static data:

            tab_names: [
                {raw: 'functions_list', readable: 'Functions'},
                {raw: 'strings_list', readable: 'Strings'},
                {raw: 'file_headers', readable: 'Headers'}
            ],

            functions_list_columns: [
                {name: 'Name', raw: 'name', is_searcheable: 'rawstring'},
                {name: 'Offset', raw: 'offset', is_searcheable: 'offset'},
                {name: 'Size', raw: 'size', is_searcheable: 'no'}
            ],

            file_headers_columns: [
                {name: 'Field', raw: 'field'},
                {name: 'Value', raw: 'value'}
            ]
        };
    },

    props: {
        table_data_map: Object,
        current_function: Number
    },

    emits: [
        'select_function',
        'load_table'
    ],

    components: {
        SearchableTable
    },

    methods: {
        load_table(...args) {
            this.$emit('load_table', ...args);
        },
        select_function(function_id) {
            this.$emit('select_function', function_id);
        }
    },

    template: `<div class="tab_view" id="side_pane">
        <div class="tab_list">
            <template v-for="tab of tab_names">
                <div :class="tab.raw == current_tab ? 'tab tab_current' : 'tab'"
                    @click="current_tab = tab.raw">
                    {{ tab.readable }}
                </div>
            </template>
        </div>
        <div class="tab_contents searcheable_table_layout">
            <template v-if="current_tab == 'functions_list'">
                <SearchableTable    
                    :table_data_map="table_data_map"
                    table_name="functions_list"
                    custom_css_class="functions_table"
                    :selected_row_index="current_function"

                    @load_table="load_table"
                    @select_row="select_function" />
            </template>
            <template v-else-if="current_tab == 'file_headers'">
                <SearchableTable
                    :table_data_map="table_data_map"
                    table_name="header_info"
                    custom_css_class="file_headers_table"
                    :selected_row_index="null"

                    @load_table="load_table" />
            </template>
        </div>
    </div>`
};