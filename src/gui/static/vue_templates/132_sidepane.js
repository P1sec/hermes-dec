var SidePane = {
    data() {
        return {
            current_tab: 'functions_list',

            // Static data:

            tab_names: [
                {raw: 'functions_list', readable: 'Functions'},
                {raw: 'strings_list', readable: 'Strings'},
                {raw: 'file_headers', readable: 'Headers'}
            ]
        };
    },

    props: {
        functions_list: Array,
        current_function: Number
    },

    emits: ['select_function'],

    components: {
        FunctionsList
    },

    methods: {
        select_function(function_id) {
            this.$emit('select_function', function_id);
        }
    },

    template: `<div id="side_pane">
        <div class="tab_view">
            <div class="tab_list">
                <template v-for="tab of tab_names">
                    <div :class="tab.raw == current_tab ? 'tab tab_current' : 'tab'"
                        @click="current_tab = tab.raw">
                        {{ tab.readable }}
                    </div>
                </template>
            </div>
            <div class="tab_contents">
                <template v-if="current_tab == 'functions_list'">
                    <FunctionsList
                        :functions_list="functions_list"
                        :current_function="current_function"
                        @select_function="select_function" />
                </template>
            </div>
        </div>
    </div>`
};