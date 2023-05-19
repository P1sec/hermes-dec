
// WIP ...

// This abstracts the rendering of graph edges, that will be
// operated through drawing a SVG background under the
// grid-positioned divs of the disassembly output

// Global state for the graph
class Graph {
    constructor(svg_root, grid_root) {
        this.svg_root = svg_root; // DOMElement
        this.grid_root = grid_root; // DOMElement

        this.css_grid = {}; // Object<Object<Union<Node, Lattice>>> - Nested/associative x,y 2D array

        this.nodes = []; // Array<Node>
        this.edges = []; // Array<Edge>
        this.lattices = []; // Array<Lattice>
    }

    get_lattice(grid_x, grid_y) {
        if(this.css_grid[grid_x] && this.css_grid[grid_x][grid_y]) {
            return this.css_grid[grid_x][grid_y];
        }
        else {
            return new Lattice(this, grid_x, grid_y);
        }
    }

    prerender() {
        for(let edge of this.edges) {
            edge.prerender();
        }
    }

    render() {
        for(let edge of this.edges) {
            edge.render();
        }

        this.svg_root.setAttribute('width', this.grid_root.scrollWidth);
        this.svg_root.setAttribute('height', this.grid_root.scrollHeight);

        this.grid_root.style.position = 'static';
    }
}