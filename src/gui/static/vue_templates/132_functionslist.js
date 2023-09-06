var FunctionsList = {
    props: {
        functions_list: Array,
        current_function: Number
    },

    emits: ['select_function'],

    template: `<div id="side_pane">
    <div id="functions_list">
        <table id="functions_table">
            <tbody>
                <template v-for="(func, index) in functions_list">
                    <tr :class="index == current_function ? 'selected_fun' : 'unselected_fun'"
                        @click="$emit('select_function', index)">
                        <td>{{ func.name }}</td>
                        <td>{{ func.offset }}</td>
                        <td>{{ func.size }}</td>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
</div>`
};