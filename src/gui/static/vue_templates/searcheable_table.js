// Put here a paginated and searchable table.

var SearcheableTable = {
    props: {
        has_search_bar: Boolean,
        columns: Array, // of {raw: String, readable: String, is_searcheable: Boolean} Objects
        rows: Array, // of Arrays of Strings
        selected_row_index: Number, // or Null
    },
    // WIP ..
    
    template: `<div>
</div>`
};