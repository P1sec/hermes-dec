// Put here a paginated and searchable table.

var SearchableTable = {
    props: {
        has_search_bar: Boolean,
        columns: Array, // of {name: String, raw: String, is_searcheable: Boolean} Objects
        rows: Array, // of Objects mapping raw proprerties Strings to value Strings

        has_pagination: Boolean,
        pagination_thresold: Number,

        has_visible_headers: Boolean,

        has_selectable_rows: Boolean,
        selected_row_index: Number, // or null
    },
    // WIP ..
    
    template: `<div class="search_bar" v-if="has_search_bar">
            🔎 <input type="text">
                <span style="font-size: 12px; vertical-align: top">
                    | Page XX / XX
                    <input type="button" value="&lt;">
                    <input type="button" value="&gt;">
                </span>
        </div>
        <div class="scrollable_area">
            <table :class="'searchable_table' + (has_selectable_rows ? ' selectable_table' : ' unselectable_table')">
                <thead v-if="has_visible_headers">
                    <tr>
                        <th v-for="column in columns">
                            {{ column.name }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="(row, index) in rows">
                        <tr :class="index === selected_row_index ? 'selected_row' : 'unselected_row'"
                            @click="$emit('select_row', index)">
                            <td v-for="cell in columns">
                                {{ row[cell.raw] }}
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>`
};