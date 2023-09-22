// Put here a paginated and searchable table.

var SearchableTable = {
    props: {
        table_data_map: Object, // <-- Associative array mapping table names (Strings) to the
            // latest "table_model" Websocket response (Object) received from the server (see
            // the "GUI server websocket protocol.md" file)
        table_name: String,

        custom_css_class: String,

        selected_row_index: Number, // or null
        search_query: String
    },

    mounted() {
        if(!this.table_data_map || !this.table_data_map[this.table_name]) {
            var text_filter = this.search_query;
            var current_row = this.selected_row_index;
            var page = this.table_data_map[this.table_name].current_page;
            this.$emit('load_table', this.table_name, text_filter, current_row, page);
        }
    },

    emits: [
        'load_table',
        'select_row'
    ],
    
    template: `
        <template v-if="table_data_map && table_data_map[table_name]">
            <div class="search_bar" v-if="table_data_map[table_name].model.has_search_bar">
                    <form XX-WIP @submit="">
                🔎      <input type="text" v-model="search_query">
                    </form>
                    <span style="font-size: 12px; vertical-align: top"
                        v-if="table_data_map[table_name].model.has_pagination">
                        | Page {{ table_data_map[table_name].current_page }} /
                        {{ table_data_map[table_name].pages }}
                        <input type="button" value="&lt;" @click="alert('TODO')">
                        <input type="button" value="&gt;" @click="alert('TODO')">
                    </span>
            </div>
            <div class="scrollable_area">
                <table :class="'searchable_table ' + (table_data_map[table_name].model.has_selectable_rows ?
                    'selectable_table ' : 'unselectable_table ') + custom_css_class">
                    <thead v-if="table_data_map[table_name].model.has_visible_headers">
                        <tr>
                            <th v-for="column in columns">
                                {{ column.name }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="row in table_data_map[table_name].displayed_rows">
                            <tr :class="row.index === selected_row_index ? 'selected_row' : 'unselected_row'"
                                @click="$emit('select_row', row.index)">
                                <td v-for="cell in row.cells">
                                    {{ cell }}
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </template>
        <div v-else>
            (Loading... <img src="spinner_gif.gif" width="24" style="vertical-align: middle"> )
        </div>
`
};