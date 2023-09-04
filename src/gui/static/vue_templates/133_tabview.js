var TabView = {
    props: {
        current_tab: String
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

    emits: ['set_current_tab'],

    template: `<div class="tab_view">
        <template v-for="tab of tab_names">
            <div :class="tab.raw == current_tab ? 'tab tab_current' : 'tab'"
                @click="$emit('set_current_tab', tab.raw)">
                {{ }}
            </div>
        </template>
    </div>`
};