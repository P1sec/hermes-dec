
// WIP ...

const SVG_NS = 'http://www.w3.org/2000/svg';
const SPACING_BETWEEN_EDGES_PX = 4;
const LINE_WIDTH = 1;

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

    get_horizontal_lattice(grid_x, grid_y) {
        if(this.css_grid[grid_x] && this.css_grid[grid_x][grid_y]) {
            return this.css_grid[grid_x][grid_y];
        }
        else {
            return new HorizontalLattice(this, grid_x, grid_y);
        }
    }

    get_vertical_lattice(grid_x, grid_y) {
        if(this.css_grid[grid_x] && this.css_grid[grid_x][grid_y]) {
            return this.css_grid[grid_x][grid_y];
        }
        else {
            return new VerticalLattice(this, grid_x, grid_y);
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
    }
}

// Contains a list of OutPort of InPort objects, each linked
// to a given Edge
class Node {
    constructor(graph, html_elem, orig_idx) {
        this.graph = graph; // Graph
        this.graph.nodes.push(this);

        // Indexes in the CSS grid (1-indexed, if both indexes
        // are even it's a node, if either index is odd it's
        // a lattice)
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
    }
}

// Is bound to a given side of a node (bottom = outwards, top = inwards)
class Port {
    constructor(graph, node, is_error_handling, is_out) {
        this.graph = graph; // Graph
        this.node = node; // Node

        this.is_out = is_out; // Boolean
        this.is_error_handling = is_error_handling; // Boolean
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
        
        this.out_port = out_port; // OutPort
        this.in_port = in_port; // InPort
        out_port.edge = this;
        in_port.edge = this;

        this.is_error_handling = out_port.is_error_handling; // Boolean
        this.lattices = []; // Array<Lattice>
        this.lattice_lanes = []; // Array<LatticeLane>
        this.rendered_objects = []; // Array<RenderedObject>
    }

    prerender() {
        // WIP... fill this.lattices and this.lattice_lanes using a
        // pathfinding algorithm

        // Pathfinding algorithm:
        // 1. The first way of the path is the HorizontalLattice
        //    located under OutPort which starts the Edge.
        //    (We're reserving a first LatticeLane matched
        //     with the corresponding OutPort here.)
        // 2. Then, pick or create 0+ VerticalLattice objects in
        //    the grid up to the level of matching InPort
        // 3. Then, pick or create 1+ HorizontalLattice objects
        //    in the grid up to the level of the matching InPort
        //
        // Our path is stored in the this.lattice_lanes object
        //
        // (Reminder: our CSS grid is: 1-indexed, if both indexes
        //  are even it's a node, if either index is odd it's
        //  a lattice)

        const src_x = this.out_port.node.grid_x;
        const src_y = this.out_port.node.grid_y + 1;

        const dst_x = this.in_port.node.grid_x;
        const dst_y = this.in_port.node.grid_y - 1;

        const src_lattice = this.graph.get_horizontal_lattice(src_x, src_y);
        const dst_lattice = this.graph.get_horizontal_lattice(dst_x, dst_y);
        
        var cur_x = src_x;
        var cur_y = src_y;

        // Step 1:
        this.lattices.push(src_lattice);

        // Step 2:
        if(dst_x < src_x) {
            cur_x--; // Should we get leftwards?
        }
        else if(dst_x > src_x || dst_y != src_y) {
            cur_x++; // Should we get rightwards?
        }
        if(dst_y < src_y) {
            while(dst_y < cur_y) {
                cur_y--; // Get an even grid index
                this.lattices.push(this.graph.get_vertical_lattice(cur_x, cur_y));
                cur_y--;
            }
        }
        else if(dst_y > src_y) {
            while(dst_y > cur_y) {
                cur_y++; // Get an even grid index
                this.lattices.push(this.graph.get_vertical_lattice(cur_x, cur_y));
                cur_y++;
            }
        }

        if(dst_x < src_x) {
            while(dst_y + 1 < cur_x) {
                cur_x--; // Get an even grid index
                this.lattices.push(this.graph.get_horizontal_lattice(cur_x, cur_y));
                cur_x--;
            }
        }
        else if(dst_x > src_x) {
            while(dst_y - 1 > cur_y) {
                cur_x++; // Get an even grid index
                this.lattices.push(this.graph.get_horizontal_lattice(cur_x, cur_y));
                cur_x++;
            }
        }

        this.lattices.push(dst_lattice);

        // Allocate this.lattice_lanes from this.lattices

        for(var lattice of this.lattices) {
            if(lattice instanceof HorizontalLattice) {
                this.lattice_lanes.push(new HorizontalLatticeLane(this.edge, lattice));
            }
            else {
                this.lattice_lanes.push(new VerticalLatticeLane(this.edge, lattice));
            }
        }
        

        // (TODO : Adjust the CSS pixel padding of lattices according
        // to their number of lanes, if needed?)

        // (Now we're think in pixels rather than grid units)

        // TODO... fill this.rendered_objects from this.lattice_lanes

        var canvas_div = this.graph.svg_root;
        var canvas_bbox = canvas_div.getBoundingClientRect();

        var src_div = this.out_port.node.html_elem.querySelector('.graph_node');
        var src_bbox = src_div.getBoundingClientRect();

        var dst_div = this.in_port.node.html_elem.querySelector('.graph_node');
        var dst_bbox = dst_div.getBoundingClientRect();

        // The start of the edge we will draw:
        var cur_x = src_bbox.x - canvas_bbox.x + src_bbox.width / 2; // In pixels now
        var cur_y = src_bbox.y - canvas_bbox.y + src_bbox.height;

        // The end of the edge we will draw:
        var target_x = dst_bbox.x - canvas_bbox.x + dst_bbox.width / 2;
        var target_y = dst_bbox.y - canvas_bbox.y;

        for(var lattice_lane of this.lattice_lanes) {
            if(lattice_lane instanceof VerticalLatticeLane) {
                cur_y += SPACING_BETWEEN_EDGES_PX + LINE_WIDTH; // WIP ..
            }
        }
        this.rendered_objects.push();
        // WIP ..
    }

    render() {
        for(let rendered_object of this.rendered_objects) {
            rendered_object.render(); // TODO...
        }
    }
}

// May be linked with a side of Node
class Lattice {
    constructor(graph, grid_x, grid_y, is_vertical) {
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
    }
}

class VerticalLattice extends Lattice {
    constructor(graph, grid_x, grid_y) {
        super(graph, grid_x, grid_y, true);
    }
}

class HorizontalLattice extends Lattice {
    constructor(graph, grid_x, grid_y) {
        super(graph, grid_x, grid_y, false);
    }
}

// Part of a Lattice and of a specific Edge
class LatticeLane {
    constructor(edge, lattice, is_vertical) {
        this.edge = edge; // Edge
        this.lattice = lattice; // Lattice

        this.is_vertical = is_vertical; // Boolean
    }

    get_lane_index() {
        return this.lattice.lanes.indexOf(this);
    }
}

class VerticalLatticeLane extends LatticeLane { // Part of a VerticalLattice, and of a specific Edge
    constructor(edge, lattice) {
        super(edge, lattice, true);
        lattice.lanes.push(this);
    }
}

class HorizontalLatticeLane extends LatticeLane { // Part of a HorizontalLattice, and of a specific Edge
    constructor(edge, lattice) {
        super(edge, lattice, false);
        lattice.lanes.unshift(this);
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

class VerticalLine extends RenderedObject {
    constructor(svg_root, x, y1, y2) {
        this.svg_root = svg_root; // DOMElement
        this.x = x;
        this.y1 = y1;
        this.y2 = y2;
    }
}

class HorizontalLine extends RenderedObject {
    constructor(svg_root, x1, x2, y) {
        this.svg_root = svg_root; // DOMElement
        this.x1 = x1;
        this.x2 = x2;
        this.y = y;
    }
}

// All the arrows should be bottom-leaning I think
class BottomLeaningArrow extends RenderedObject {
    constructor(svg_root, tip_x, tip_y) {
        this.svg_root = svg_root; // DOMElement;
        this.tip_x = tip_x;
        this.tip_y = tip_y;
    }
}

// Later:
/**
class OverlapHalfCircle extends RenderedObject {

}
*/