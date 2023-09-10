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
                {name: 'Name', raw: 'name', is_searcheable: true},
                {name: 'Offset', raw: 'offset', is_searcheable: true},
                {name: 'Size', raw: 'size', is_searcheable: true}
            ],

            file_headers_columns: [
                {name: 'Field', raw: 'field'},
                {name: 'Value', raw: 'value'}
            ]
        };
    },

    props: {
        functions_list: Array,
        header_info: Array,
        current_function: Number
    },

    emits: ['select_function'],

    components: {
        SearchableTable
    },

    methods: {
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
                    :has_search_bar="true"
                    :columns="functions_list_columns"
                    :rows="functions_list"
                    :has_pagination="true"
                    :pagination_thresold="350"
                    custom_class="functions_table"
                    :has_visible_headers="true"
                    :has_selectable_rows="true"
                    :selected_row_index="current_function"
                    @select_row="select_function" />
            </template>
            <template v-else-if="current_tab == 'file_headers'">
                <SearchableTable
                    :has_search_bar="false"
                    :columns="file_headers_columns"
                    :rows="header_info"
                    :has_pagination="false"
                    :pagination_thresold="null"
                    custom_class="file_headers_table"
                    :has_visible_headers="true"
                    :has_selectable_rows="false"
                    :selected_row_index="null" />
            </template>
        </div>
    </div>`
};