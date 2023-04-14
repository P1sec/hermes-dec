
// WIP ...

const SVG_NS = 'http://www.w3.org/2000/svg';

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

    prerender() {
        for(let edge of this.edges) {
            edge.prerender();
        }
    }

    render() {
        for(let edge of this.edges) {
            edge.render();
        }
    }
}

// Contains a list of OutPort of InPort objects, each linked
// to a given Edge
class Node {
    constructor(graph, html_elem, orig_idx) {
        this.graph = graph; // Graph
        this.graph.nodes.push(this);

        // Indexed in the CSS grid (1-indexed, odd index = node, even index = lattice)
        this.grid_x = html_elem.style.gridColumn; // Integer
        this.grid_y = html_elem.style.gridRow; // Integer
        
        if(!this.graph.css_grid[this.grid_x]) {
            this.graph.css_grid[this.grid_x] = {};
        }
        this.graph.css_grid[this.grid_x][this.grid_y] = this;

        this.html_elem = html_elem; // DOMElement
        this.orig_idx = orig_idx; // Integer
        this.in_ports = []; // Array<InPort>
        this.out_ports = []; // Array<OutPort>

        this.bottom_lattice = new HorizontalLattice(graph, this, false);
        if(this.html_elem.gridRow == 0) {
            this.top_lattice = new HorizontalLattice(graph, this, true);
        }
        else {
            this.top_lattice = null;
        }
        this.right_lattice = new VerticalLattice(graph, this, false);
    }
}

// Is bound to a given side of a node (bottom = outwards, top = inwards)
class Port {
    constructor(graph, node, is_error_handling, is_out) {
        this.graph = graph; // Graph

        this.is_out = is_out; // Boolean
        this.is_error_handling = is_error_handling; // Boolean
        this.node = node; // Node
        if(is_out) {
            node.out_ports.push(this);
        }
        else {
            node.in_ports.push(this);
        }
        this.edge = null; // Edge, to be filled when constructing the said Edge
    }
}

class OutPort extends Port { // Rendered at the bottom of nodes
    constructor(graph, node, is_error_handling) {
        super(graph, node, is_error_handling, true);
    }
}

class InPort extends Port { // Rendered at the top of nodes
    constructor(graph, node, is_error_handling) {
        super(graph, node, is_error_handling, false);
    }
}

// Links an OutPort to a InPort, composed of a path of LatticeLane
// objects
class Edge {
    constructor(graph, out_port, in_port) {
        this.graph = graph; // Graph
        this.graph.edges.push(this);
        
        out_port.edge = this;
        in_port.edge = this;

        this.is_error_handling = out_port.is_error_handling; // Boolean
        this.lattice_lanes = []; // Array<LatticeLane>
        this.rendered_objects = []; // Array<RenderedObject>
    }

    prerender() {
        // TODO... fill this.lattice_lanes using a pathfinding algorithm

        // TODO... fill this.rendered_objects
    }

    render() {
        for(let rendered_object of this.rendered_objects) {
            rendered_object.render(); // TODO...
        }
    }
}

// Linked with a side of Node
class Lattice {
    constructor(graph, node, is_before, grid_x, grid_y, is_vertical) {
        this.graph = graph; // Graph
        graph.lattices.push(this);

        this.grid_x = grid_x;
        this.grid_y = grid_y;

        this.grid_element = document.createElement('div');
        this.grid_element.style.gridColumn = this.grid_x; // Set by the caller constructor, 1-indexed
        this.grid_element.style.gridRow = this.grid_y; // Same

        if(!this.graph.css_grid[this.grid_x]) {
            this.graph.css_grid[this.grid_x] = {};
        }
        this.graph.css_grid[this.grid_x][this.grid_y] = this;
        
        this.graph.grid_root.appendChild(this.grid_element);

        this.lanes = []; // Array<LatticeLane>

        this.is_before = is_before; // Boolean
        this.is_vertical = is_vertical; // Boolean

        this.all_neighbors = []; // Array<Lattice>
    }
}

class VerticalLattice extends Lattice { // Rendered at the right of each Node
    constructor(graph, node, is_before) {
        if(is_before) {
            var grid_x = node.grid_x - 1;
        }
        else {
            var grid_x = node.grid_x + 1;
        }
        var grid_y = node.grid_y;

        super(graph, node, is_before, grid_x, grid_y, true);

        // Neighbour lattices, used for pathfinding:
        this.tl_lattice = null; // HorizontalLattice - top-left
        this.tc_lattice = null; // VerticalLattice - top-center
        this.tr_lattice = null; // HorizontalLattice - top-right

        this.bl_lattice = null; // HorizontalLattice - bottom-left
        this.bc_lattice = null; // VerticalLattice - bottom-center
        this.br_lattice = null; // HorizontalLattice - bottom-right
    }
}

class HorizontalLattice extends Lattice { // Rendered under each Node, and atop of the first-row Node objects
    constructor(graph, node, is_before) {
        var grid_x = node.grid_x;
        if(is_before) {
            var grid_y = node.grid_y - 1;
        }
        else {
            var grid_y = node.grid_y + 1;
        }

        super(graph, node, is_before, grid_x, grid_y, false);

        // Neighbour lattices, used for pathfinding:
        this.lt_lattice = null; // VerticalLattice - left-top
        this.lc_lattice = null; // HorizontalLattice - left-center
        this.lb_lattice = null; // VerticalLattice - left-bottom
        
        this.rt_lattice = null; // VerticalLattice - right-top
        this.rc_lattice = null; // HorizontalLattice - right-center
        this.rb_lattice = null; // VerticalLattice - right-bottom
    
    }
}

// Part of a Lattice and of a specific Edge
class LatticeLane {
    constructor(edge, lattice, is_vertical) {
        this.edge = edge; // Edge

        this.lattice = lattice; // Lattice
        lattice.lanes.push(this);

        this.is_vertical = is_vertical; // Boolean
    }
}

class VerticalLatticeLane extends LatticeLane { // Part of a VerticalLattice, and of a specific Edge
    constructor(edge, lattice) {
        super(edge, lattice, true);
    }
}

class HorizontalLatticeLane extends LatticeLane { // Part of a HorizontalLattice, and of a specific Edge
    constructor(edge, lattice) {
        super(edge, lattice, false);
    }
}

// Will be rendered onto the SVG canvas, each LatticeLane contains
// one or more, has geometrical references to other objects
class RenderedObject {
    constructor(graph) {
        this.graph = graph; // Graph
    }

    render() {
        // TODO...
    }
}

class VerticalPortLine extends RenderedObject {
    constructor(svg_root, x1, y1, x2, y2) {
        this.svg_root = svg_root; // DOMElement
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
    }
}

class VerticalLatticeLine extends RenderedObject {
    
}

class HorizontalLatticeLine extends RenderedObject {

}

// All the arrows should be bottom-leaning I think
class BottomLeaningArrow extends RenderedObject {
    
}

class OverlapHalfCircle extends RenderedObject {

}