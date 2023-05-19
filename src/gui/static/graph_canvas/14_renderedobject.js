
const SVG_NS = 'http://www.w3.org/2000/svg';

// Will be rendered onto the SVG canvas, each LatticeLane contains
// one or more, has geometrical references to other objects
class RenderedObject {
    constructor(svg_root) {
        this.svg_root = svg_root; // DOMElement
    }
}

class Curve extends RenderedObject {
    constructor(svg_root, css_color, x1, x2, y1, y2, invert) {
        super(svg_root);
        this.css_color = css_color;
        this.x1 = x1;
        this.x2 = x2;
        this.y1 = y1;
        this.y2 = y2;
        this.invert = invert;
    }

    render() {
        var element = document.createElementNS(SVG_NS, 'path');

        var x_middle = this.x1 + (this.x2 - this.x1) / 3;
        var y_middle = this.y1 + (this.y2 - this.y1) / 3;

        var path_string = 'M ' + this.x1 + ' ' + this.y1 + ' ';
        if(!this.invert) {
            path_string += 'Q ' + this.x1 + ' ' + y_middle + ' ' + x_middle + ' ' + y_middle + ' ';
            path_string += 'Q ' + this.x2 + ' ' + y_middle + ' ' + this.x2 + ' ' + this.y2;
        }
        else {
            path_string += 'Q ' + x_middle + ' ' + this.y1 + ' ' + x_middle + ' ' + y_middle + ' ';
            path_string += 'Q ' + x_middle + ' ' + this.y2 + ' ' + this.x2 + ' ' + this.y2;
        }

        element.setAttribute('d', path_string);
        element.setAttribute('fill', 'none');
        element.setAttribute('stroke', this.css_color);
        element.setAttribute('stroke-width', LINE_WIDTH);

        this.svg_root.appendChild(element);
    }
}

class Line extends RenderedObject {
    constructor(svg_root, css_color, x1, x2, y1, y2) {
        super(svg_root);
        this.css_color = css_color;
        this.x1 = x1;
        this.x2 = x2;
        this.y1 = y1;
        this.y2 = y2;
    }

    render() {
        var element = document.createElementNS(SVG_NS, 'line');
        
        element.setAttribute('stroke', this.css_color);
        element.setAttribute('stroke-width', LINE_WIDTH);
        element.setAttribute('x1', Math.round(this.x1));
        element.setAttribute('x2', Math.round(this.x2));
        element.setAttribute('y1', Math.round(this.y1));
        element.setAttribute('y2', Math.round(this.y2));
        
        this.svg_root.appendChild(element);
    }

}

class DebugMarkerCross extends RenderedObject {
    constructor(svg_root, css_color, x, y, text_label) {
        super(svg_root);
        this.css_color = css_color;
        this.x = x;
        this.y = y;
        this.text_label = text_label;
    }

    render() {
        var element = document.createElementNS(SVG_NS, 'path');

        var line_width = 2; // In pixels
        var arm_size = 9; // In pixels

        var cur_x = this.x - arm_size;
        var cur_y = this.y - arm_size;
        var path = 'M ' + cur_x + ' ' + cur_y + ' ';
        cur_x += arm_size * 2;
        cur_y += arm_size * 2;
        path += 'L ' + cur_x + ' ' + cur_y + ' ';
        
        cur_x -= arm_size * 2;
        path += 'M ' + cur_x + ' ' + cur_y + ' ';
        cur_y -= arm_size * 2;
        cur_x += arm_size * 2;
        path += 'L ' + cur_x + ' ' + cur_y + ' ';

        element.setAttribute('stroke', this.css_color);
        element.setAttribute('stroke-width', line_width);
        element.setAttribute('d', path);

        this.svg_root.appendChild(element);

        var element = document.createElementNS(SVG_NS, 'text');
        
        element.appendChild(document.createTextNode(this.text_label));
        
        element.setAttribute('dominant-baseline', 'middle');
        element.setAttribute('fill', this.css_color);
        element.style.font = '24px sans-serif';
        element.setAttribute('x', this.x + arm_size * 2.5);
        element.setAttribute('y', this.y);

        this.svg_root.appendChild(element);
    }
}

// All the arrows should be bottom-leaning I think
class BottomLeaningArrow extends RenderedObject {
    constructor(svg_root, css_color, tip_x, tip_y) {
        super(svg_root);
        this.css_color = css_color;
        this.tip_x = tip_x;
        this.tip_y = tip_y;
    }

    render() {
        var element = document.createElementNS(SVG_NS, 'polygon');

        var points = '';
        var line_size = 14;

        var x = this.tip_x - line_size / 2;
        var y = this.tip_y - line_size / 2;
        
        points += x + ' ' + y + ',';
        x += line_size;
        points += x + ' ' + y + ',';
        x -= line_size / 2;
        y += line_size / 2;
        points += x + ' ' + y;

        element.setAttribute('fill', this.css_color);

        element.setAttribute('points', points);

        this.svg_root.appendChild(element);
    }
}

// Later:
/**
class OverlapHalfCircle extends RenderedObject {

}
*/