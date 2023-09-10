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
                {raw: ''}
            ]
        };
    },

    props: {
        functions_list: Array,
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
                    :has_visible_headers="true"
                    :has_selectable_rows="true"
                    :selected_row_id="current_function"
                    @select_row="select_function" />
            </template>
        </div>
    </div>`
};