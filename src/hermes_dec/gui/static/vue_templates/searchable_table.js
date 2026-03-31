// Put here a paginated and searchable table.

var SearchableTable = {
    props: {
        table_data_map: Object, // <-- Associative array mapping table names (Strings) to the
            // latest "table_model" Websocket response (Object) received from the server (see
            // the "GUI server websocket protocol.md" file)
        table_name: String,

        custom_css_class: String,

        selected_row_index: Number // or null
    },

    mounted() {
        if(!this.table_data_map || !this.table_data_map[this.table_name]) {
            var page = 1;
            this.$emit('load_table', this.table_name, this.search_query, this.selected_row_index, page);
        }
    },

    methods: {
        search_query_submit(event) {
            event.preventDefault();

            var page = 1;
            this.$emit('load_table', this.table_name, this.search_query, this.selected_row_index, page);

            return false;
        },

        prev_page() {
            var page = this.table_data_map[this.table_name].current_page;
            page = Math.max(1, page - 1);
            this.$emit('load_table', this.table_name, this.search_query, this.selected_row_index, page);
        },

        next_page() {
            var page = this.table_data_map[this.table_name].current_page;
            page = Math.min(this.table_data_map[this.table_name].pages, page + 1);
            this.$emit('load_table', this.table_name, this.search_query, this.selected_row_index, page);
        }
    },

    emits: [
        'load_table',
        'select_row'
    ],
    
    template: `
        <template v-if="table_data_map && table_data_map[table_name]">
            <div class="search_bar" v-if="table_data_map[table_name].model.has_search_bar">
                    <form @submit="search_query_submit" style="display: inline-block">
                        <input type="text" v-model="search_query" style="width: 144px; margin-right: 4px">
                        <input type="submit" value="🔎">
                    </form>
                    <span style="font-size: 12px; vertical-align: top"
                        v-if="table_data_map[table_name].model.has_pagination">
                        | Page {{ table_data_map[table_name].current_page }} /
                        {{ table_data_map[table_name].pages }}
                        <template v-if="table_data_map[table_name].current_page > 1">
                            <input type="button" value="&lt;" @click="prev_page">
                        </template>
                        <template v-else>
                            <input type="button" value="&lt;" disabled>
                        </template>
                        <template v-if="table_data_map[table_name].current_page < table_data_map[table_name].pages">
                            <input type="button" value="&gt;" @click="next_page">
                        </template>
                        <template v-else>
                            <input type="button" value="&gt;" disabled>
                        </template>
                    </span>
            </div>
            <div class="scrollable_area" v-if="!table_data_map[table_name].reloading">
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
                            <tr :class="row.id === selected_row_index ? 'selected_row' : 'unselected_row'"
                                @click="$emit('select_row', row.id)">
                                <td v-for="cell in row.cells">
                                    {{ cell }}
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </template>
        <div v-if="!table_data_map || !table_data_map[table_name] || table_data_map[table_name].reloading">
            (Loading... <img src="spinner_gif.gif" width="24" style="vertical-align: middle"> )
        </div>
`
};