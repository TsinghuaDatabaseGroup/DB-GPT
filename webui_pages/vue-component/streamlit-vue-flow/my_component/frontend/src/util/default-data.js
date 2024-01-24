const defaultOptions = {
  layout: {
    type: 'dagreLayout',
    options: {
      rankdir: 'LR',
      nodesep: 30,
      ranksep: 60,
      controlPoints: true,
    },
  },
  disLinkable: false, // 可删除连线
  linkable: false,    // 可连线
  draggable: true,   // 可拖动
  zoomable: true,    // 可放大
  moveable: true,    // 可平移
  theme: {
    edge: {
      shapeType: 'AdvancedBezier',
      isExpandWidth: false,
    },
    autoResizeRootSize: false
  }
};

export {
  defaultOptions,
};
