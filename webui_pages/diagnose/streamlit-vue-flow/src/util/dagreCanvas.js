import _ from 'lodash';
import {Canvas, Layout} from 'butterfly-dag';

class DagreCanvas extends Canvas {
  drageReDraw(newParam) {
    const {nodes, layout, edges} = this;
    const addResultNodes = nodes.map((item) => {
      return item.options;
    });
    if (newParam) {
      layout.options = {
        ...layout.options,
        ...newParam
      };
    }
    Layout.dagreLayout({
      rankdir: (newParam && newParam.rankdir) || _.get(layout, 'options.rankdir') || 'TB',
      align: (newParam && newParam.align) || _.get(layout, 'options.align'),
      nodeSize: (newParam && newParam.nodeSize) || _.get(layout, 'options.nodeSize'),
      nodesepFunc: (newParam && newParam.nodesepFunc) || _.get(layout, 'options.nodesepFunc'),
      ranksepFunc: (newParam && newParam.ranksepFunc) || _.get(layout, 'options.ranksepFunc'),
      nodesep: (newParam && newParam.nodesep) || _.get(layout, 'options.nodesep') || 50,
      ranksep: (newParam && newParam.ranksep) || _.get(layout, 'options.ranksep') || 50,
      controlPoints: (newParam && newParam.controlPoints) || _.get(layout, 'options.controlPoints') || false,
      data: {
        nodes: addResultNodes,
        edges: edges.map(item => ({
          source: item.sourceNode.id,
          target: item.targetNode.id
        }))
      }});
    // 布局计算完位置后left和top赋值给node节点
    nodes.forEach((item, index) => {
      const currentNodeNewLeft = addResultNodes[index].left;
      const currentNodeNewTop = addResultNodes[index].top;
      const currentNodeNewPosInfo = addResultNodes[index].posInfo;
      if (item.top !== currentNodeNewTop || item.left !== currentNodeNewLeft) {
        item.options.top = currentNodeNewTop;
        item.options.left = currentNodeNewLeft;
        item.options.posInfo = currentNodeNewPosInfo;
        item.moveTo(currentNodeNewLeft, currentNodeNewTop);
      }
    });
  }
}

export default DagreCanvas;
