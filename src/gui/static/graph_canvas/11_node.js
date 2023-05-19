

// Contains a list of OutPort of InPort objects, each linked
// to a given Edge
class Node {
    constructor(graph, grid_element, orig_idx) {
        this.graph = graph; // Graph
        this.graph.nodes.push(this);

        // (Reminders about our CSS grid: indexes begin at 1; for a
        //  given entry, if both indexes are even it's a node, if
        //  either index is odd it's a lattice)
        this.grid_x = parseInt(grid_element.style.gridColumn, 10); // Integer
        this.grid_y = parseInt(grid_element.style.gridRow, 10); // Integer
        
        if(!this.graph.css_grid[this.grid_x]) {
            this.graph.css_grid[this.grid_x] = {};
        }
        this.graph.css_grid[this.grid_x][this.grid_y] = this;

        this.grid_element = grid_element; // DOMElement
        this.orig_idx = orig_idx; // Integer
        this.in_ports = []; // Array<InPort>
        this.out_ports = []; // Array<OutPort>
    }
}