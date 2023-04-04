
// WIP ...

// NOTE : We'll rather likely not use canvas at all but CSS/HTML for rendering
// a tiled thing in a scrolled window with text divs + kind of overlap testing
// (and SVG icons as background for tiles of the graph?)

// Intersection/overlay testing can use the equivalent of a 2D array of booleans
// (maybe stored as a hash map or just an array or coordinates?) Pathfinding?

const TILE_SIDE = 5; // Use 5*5 square as a base unit for placing graphes and edges

// Used by the Block class below.
const BlockType = Object.freeze({
    NODE: Symbol('node'),
    EDGE_START: Symbol('edge_start'),
    EDGE_MIDDLE: Symbol('edge_middle'),
    EDGE_END: Symbol('edge_end')
});

// Class representing a tiled rectangle.
// Either represents a node of the graph or a continuous rectangle part of an edge.
// The graph is directed.
//
// Ideally, we should traverse the graph many times while there is any overlap and
// attempt to use sufficient initial spacing between to make any overlap unlikely.
class Block {
    constructor() {
        this.min_x = null; // Number
        this.min_y = null; // Number
        this.max_x = null; // Number
        this.max_y = null; // Number

        // this.
    }

    set_area_for_edge() {

    }
}

let x_y_coord_to_block = {}; // {'x,y' formatted String: Block}