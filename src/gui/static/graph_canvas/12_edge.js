

const LINE_WIDTH = 2;
const SPACING_BETWEEN_EDGES_PX = 25;
const LANE_PX_SIZE = SPACING_BETWEEN_EDGES_PX + LINE_WIDTH;

// Links an OutPort to a InPort, composed of a path of LatticeLane
// objects
class Edge {
    constructor(graph, out_port, in_port) {
        this.edge_color = 'hwb(' + Math.round((graph.edges.length * 62) % 360) + ' 10% 20%)';

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
        this.lattices = [];
        this.lattice_lanes = [];
        this.rendered_objects = [];

        // WIP... fill this.lattices and this.lattice_lanes using a
        // pathfinding algorithm

        // Pathfinding algorithm:
        // 1. The first way of the path is the horizontal Lattice (*)
        //    located under OutPort which starts the Edge.
        //    (We're reserving a first LatticeLane matched
        //     with the corresponding OutPort here.)
        // 2. Then, pick or create 0+ vertical Lattice (**) objects
        //    in the grid up to the level of matching InPort
        // 3. Then, pick or create 1+ horizontal Lattice (*) objects
        //    in the grid up to the level of the matching InPort
        //
        // (*) horizontal Lattice objects host horizontal LatticeLane
        // objects which match (optionally: a vertical Line RenderedObject
        // going out/in from a Port, plus in all cases) a horizontal Line
        // RenderedObject going either leftwards or rightwards.
        //
        // (**) vertical Lattice objects host vertical LatticeLane
        // objects which match a vertical Line RenderedObject
        // connected to the horizontal Line of an horizontal Lattice.
        //
        // Our path is stored in the this.lattice_lanes object
        //
        // (Reminders about our CSS grid: indexes begin at 1; for a
        //  given entry, if both indexes are even it's a node, if
        //  either index is odd it's a lattice)

        const src_x = this.out_port.node.grid_x;
        const src_y = this.out_port.node.grid_y + 1;

        const dst_x = this.in_port.node.grid_x;
        const dst_y = this.in_port.node.grid_y - 1;

        const src_lattice = this.graph.get_lattice(src_x, src_y);
        const dst_lattice = this.graph.get_lattice(dst_x, dst_y);

        var sort_key = dst_x * 1024 + dst_y;
        
        var cur_x = src_x;
        var cur_y = src_y;

        // Step 0: Check for short paths (a block where we should just
        // draw a vertical line towards the bottom neighbor)

        var is_short_path = false;

        if(src_x == dst_x) {
            is_short_path = true;
            
            var x = dst_x;
            var min_y = Math.min(src_y, dst_y) + 1;
            var max_y = Math.max(src_y, dst_y);

            for(var y = min_y; y < max_y; y++) {
                if(this.graph.css_grid[x] && this.graph.css_grid[x][y]) {
                    is_short_path = false;
                    break;
                }
            }
        }

        // Step 1:
        this.lattices.push(src_lattice);

        if(dst_x < src_x) {
            cur_x--; // Should we get leftwards?
            this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
        }
        else if(!is_short_path) {
            cur_x++; // Should we get rightwards?
            this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
        }

        if(dst_y < src_y) {
            while(dst_y < cur_y) {
                cur_y--; // Get an even grid index
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
                cur_y--;
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
            }
        }
        else if(dst_y > src_y) {
            while(dst_y > cur_y) {
                cur_y++; // Get an even grid index
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
                cur_y++;
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
            }
        }

        if(dst_x < src_x) {
            while(dst_x + 1 < cur_x) {
                cur_x--; // Get an even grid index
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
                cur_x--;
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
            }
        }
        else if(dst_x > src_x) {
            while(dst_x - 1 > cur_x) {
                cur_x++; // Get an even grid index
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
                cur_x++;
                this.lattices.push(this.graph.get_lattice(cur_x, cur_y));
            }
        }

        this.lattices.push(dst_lattice);

        /**
         * Allocate this.lattice_lanes from this.lattices
         * 
         * (TODO: Use a consistent insertion order of the lanes inside the
         *  lattices, as described below:
         *   -- "XXX TODO ")
         */

        var prev_x = -1;
        var prev_y = -1;
        for(var lattice_idx = 0; lattice_idx < this.lattices.length; lattice_idx++) {
            var lattice = this.lattices[lattice_idx];
            var cur_x = lattice.grid_x;
            var cur_y = lattice.grid_y;
            if((cur_x !== prev_x || cur_y !== prev_y) &&
                lattice_idx === this.lattices.indexOf(lattice)) { // TODO: Useless soon?
                this.lattice_lanes.push(new LatticeLane(this.edge, lattice, sort_key));
            }
            prev_x = cur_x;
            prev_y = cur_y;
        }

        /**
         * Adjust the lattice <div> heights according to the number of present
         * lanes for each Lattice object (from this.lattices)
         */

        for(var lattice of this.lattices) {
            lattice.grid_element.style.minHeight = (LANE_PX_SIZE * lattice.lanes.length + SPACING_BETWEEN_EDGES_PX) + 'px';
            lattice.grid_element.style.minWidth = (LANE_PX_SIZE * lattice.lanes.length + SPACING_BETWEEN_EDGES_PX) + 'px';
        }
    }

    render() {
        /** 
         * WIP... fill this.rendered_objects from this.lattice_lanes
         */

        // (Now we're thinking in pixels rather than grid units)

        // (Done ABOVE : Adjust the CSS pixel padding of lattices according
        // to their number of lanes, if needed?)

        // Get the origin x,y position of the canvas:

        var canvas_div = this.graph.svg_root;
        var canvas_bbox = canvas_div.getBoundingClientRect();

        // Get the origin x1,y1,x2,y2 positions of the
        // begin and destination blocks of the graph

        var src_div = this.out_port.node.grid_element.querySelector('.graph_node');
        var src_bbox = src_div.getBoundingClientRect();

        var lane_px_offset = this.lattice_lanes[0].get_lane_index() * LANE_PX_SIZE;
        var centered_lane_px_offset = lane_px_offset - (LANE_PX_SIZE * (this.lattices[0].lanes.length - 1) / 2);

        // The start of the edge we will draw: (bottom-center of the begin block)
        var cur_x = src_bbox.x - canvas_bbox.x + src_bbox.width / 2 + centered_lane_px_offset; // In pixels now
        var cur_y = src_bbox.y - canvas_bbox.y + src_bbox.height;

        // (Draw a first vertical Line)
        
        var first_ankle_height = lane_px_offset + LANE_PX_SIZE;
        // console.log('Z ' + first_ankle_height, ' / ', this.lattice_lanes[0].get_lane_index()); // DEBUG

        this.rendered_objects.push(new Line(
                this.graph.svg_root, this.edge_color, cur_x, cur_x, cur_y, cur_y + first_ankle_height));

        cur_y += first_ankle_height;

        // DEBUG: Put debug points on the rendered map
        /* for(var i = 0; i < this.lattice_lanes.length; i++) {
            var lattice_lane = this.lattice_lanes[i];
            var div = lattice_lane.lattice.grid_element;
            var bbox = div.getBoundingClientRect();
            console.log('TT / ', i, '//', bbox.x, '/', canvas_bbox.x);
            var absolute_x = bbox.x - canvas_bbox.x;
            var absolute_y = bbox.y - canvas_bbox.y;

            var x = absolute_x + 60 * lattice_lane.get_lane_index(); // DEBUG / + 20
            var y = absolute_y; // DEBUG / + 20

            this.rendered_objects.push(new DebugMarkerCross(this.graph.svg_root, this.edge_color, x, y, i));
        } */

        // (Draw a sequence of horizontal Line, ...
        //  (1+ vertical Line/vertical Line items), ... horizontal Line)
        for(var lattice_lane of this.lattice_lanes) {

            var div = lattice_lane.lattice.grid_element;
            var bbox = div.getBoundingClientRect();

            var absolute_bbox_x_left = bbox.x - canvas_bbox.x;
            var absolute_bbox_x_right = absolute_bbox_x_left + bbox.width;
            var absolute_bbox_y_top = bbox.y - canvas_bbox.y;
            var absolute_bbox_y_bottom = absolute_bbox_y_top + bbox.height;

            var old_x = cur_x;
            
            cur_x = (absolute_bbox_x_left + absolute_bbox_x_right) / 2 + lattice_lane.get_lane_index() * LANE_PX_SIZE;
            cur_x -= (LANE_PX_SIZE * (lattice_lane.lattice.lanes.length - 1) / 2);

            var old_y = cur_y;

            cur_y = (absolute_bbox_y_top + absolute_bbox_y_bottom) / 2 + lattice_lane.get_lane_index() * LANE_PX_SIZE;
            cur_y -= (LANE_PX_SIZE * (lattice_lane.lattice.lanes.length - 1) / 2);

            // if(old_x == cur_x || old_y == cur_y) {
                this.rendered_objects.push(new Line(this.graph.svg_root, this.edge_color, old_x, cur_x, old_y, cur_y));
            /* }
            else {
                var is_horizontal = Math.abs(old_x - cur_x) > Math.abs(old_y - cur_y);
                if((is_horizontal && old_y < cur_y) || (!is_horizontal && old_x > cur_x)) {
                    this.rendered_objects.push(new Curve(this.graph.svg_root, this.edge_color, old_x, cur_x, old_y, cur_y, false));
                }
                else {
                    this.rendered_objects.push(new Curve(this.graph.svg_root, this.edge_color, old_x, cur_x, old_y, cur_y, true));
                }
            } */

        }

        var dst_div = this.in_port.node.grid_element.querySelector('.graph_node');
        var dst_bbox = dst_div.getBoundingClientRect();

        // The end of the edge we will draw: (top-center of the destination block)
        var target_y = dst_bbox.y - canvas_bbox.y;

        // (Draw a final vertical Line)
        this.rendered_objects.push(new Line(this.graph.svg_root, this.edge_color, cur_x, cur_x, cur_y, target_y));
        
        // (Draw the arrow towards the box)
        this.rendered_objects.push(new BottomLeaningArrow(this.graph.svg_root, this.edge_color, cur_x, target_y));

        for(let rendered_object of this.rendered_objects) {
            rendered_object.render();
        }
    }
}