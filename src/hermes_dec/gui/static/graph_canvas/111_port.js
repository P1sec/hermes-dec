

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