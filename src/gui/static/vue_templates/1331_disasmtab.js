var DisasmTab = {
    props: {
        current_function: Number,
        disasm_blocks: Object
    },

    mounted() {
        const canvas_grid = document.querySelector('#canvas_grid');
        canvas_grid.innerHTML = '';

        const svg_tag = document.querySelector('#canvas_svg');
        svg_tag.innerHTML = '';

        var graph = new Graph(svg_tag, canvas_grid);
        var node_objects = [];

        for(var block_idx = 0; block_idx < this.disasm_blocks.length; block_idx++) {
            var block = this.disasm_blocks[block_idx];

            var html_block = document.createElement('div');

            // We're using a 1-indexed CSS grid layout.
            // When both indexes are even it's a node,
            // when either index (row or column) is odd it's a lattice
            html_block.style.gridColumn = block.grid_x * 2;
            html_block.style.gridRow = block.grid_y * 2;
            
            var node_div = document.createElement('div');
            node_div.className = 'graph_node';
            node_div.textContent = block.text;
            html_block.appendChild(node_div);

            var node = new Node(graph, html_block, block_idx);
            node_objects.push(node);

            canvas_grid.appendChild(html_block);
        }

        for(var block_idx = 0; block_idx < this.disasm_blocks.length; block_idx++) {
            var block = this.disasm_blocks[block_idx];
            var node = node_objects[block_idx];

            for(var child_port_idx of block.child_nodes) {
                var out_port = new OutPort(graph, node, false);
                var in_port = new InPort(graph, node_objects[child_port_idx], false);
                new Edge(graph, out_port, in_port);
            }
            for(var child_port_idx of block.child_error_nodes) {
                var out_port = new OutPort(graph, node, true);
                var in_port = new InPort(graph, node_objects[child_port_idx], true);
                new Edge(graph, out_port, in_port);
            }
        }

        graph.prerender();
        graph.render();

        // WIP fix display introduce graph ordering introduce links pathfinding ...
    },

    template: `<div id="canvas">
        <svg id="canvas_svg"></svg>
        <div id="canvas_grid"></div>
    </div>`
};