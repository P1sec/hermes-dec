

// Part of a Lattice and of a specific Edge
class LatticeLane {
    constructor(edge, lattice, sort_key) {
        this.edge = edge; // Edge
        this.lattice = lattice; // Lattice
        this.sort_key = sort_key;

        this.lattice.lanes.push(this);
        this.lattice.lanes.sort(function(a, b) {
            return a.sort_key - b.sort_key;
        });
    }

    get_lane_index() {
        var ret = this.lattice.lanes.indexOf(this);
        if(ret == -1) {
            alert('[Error: indexOf returned -1]');
        }
        return ret;
    }
}
