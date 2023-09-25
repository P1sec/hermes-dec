var MainPane = {
    props: {
        current_function: Number,
        current_tab: String,
        function_is_syncing: Boolean,
        disasm_blocks: Object
    },

    data() {
        return {
            // Static data:

            tab_names: [
                {raw: 'disasm_view', readable: 'Disassembly'},
                {raw: 'string_view', readable: 'Strings'},
                {raw: 'decompile_view', readable: 'Decompiled code'}
            ]
        }
    },

    components: {
        DisasmTab
    },

    emits: ['set_current_tab'],

    template: `<div class="main_pane tab_view">
        <div class="tab_list">
            <template v-for="tab of tab_names">
                <div :class="tab.raw == current_tab ? 'tab tab_current' : 'tab'"
                    @click="$emit('set_current_tab', tab.raw)">
                    {{ tab.readable }}
                </div>
            </template>
        </div>
        <template v-if="function_is_syncing">
            <h1 style="margin-left: 26px">Loading function data...</h1>
        </template>
        <div class="tab_contents scrollable_area" v-else>
            <template v-if="current_tab == 'disasm_view' && disasm_blocks">
                <DisasmTab
                    :current_function="current_function"
                    :disasm_blocks="disasm_blocks" />
            </template>
        </div>
    </div>`
};