

// May be linked with a side of Node
class Lattice {
    constructor(graph, grid_x, grid_y) {
        this.graph = graph; // Graph
        graph.lattices.push(this);

        this.grid_x = grid_x;
        this.grid_y = grid_y;

        this.grid_element = document.createElement('div');
        this.grid_element.style.gridColumn = this.grid_x; // Set by the caller constructor, 1-indexed
        this.grid_element.style.gridRow = this.grid_y; // Same

        this.grid_element.className = 'lattice';

        if(!this.graph.css_grid[this.grid_x]) {
            this.graph.css_grid[this.grid_x] = {};
        }
        this.graph.css_grid[this.grid_x][this.grid_y] = this;
        
        this.graph.grid_root.appendChild(this.grid_element);

        this.lanes = []; // Array<LatticeLane>
    }
}
