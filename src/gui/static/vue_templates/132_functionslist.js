var FunctionsList = {
    props: {
        functions_list: Array
    },

    emits: ['TODO'],

    template: `<div id="side_pane">
    <div id="functions_list">
        <table id="functions_table">
            <tbody>
                <tr v-for="(func, index) in functions_list" @click="$emit('select_function', index)">
                    <td>{{ func.name }}</td>
                    <td>{{ func.offset }}</td>
                    <td>{{ func.size }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>`
};