import {Edge} from 'butterfly-dag';

class BaseEdge extends Edge {
  draw(obj) {
    const path = super.draw(obj);
    console.log('********path:', path);
    return path;
  }
  drawLabel(texts) {
    console.log('********texts:', texts);
  }
}

export default BaseEdge;
