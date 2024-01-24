import titleContentNode from './node/title-content-node';
import Edge from './util/edge';

// 下: [0,1]
// 上: [0,-1]
// 右: [1,0]
// 左: [-1,0]

const data = {
  nodes: [
    {
      isRoot: true,
      id: 'A',
      title: '知识库A',
      left: 20,
      right: 20,
      content: '我是知识库A 的详细内容',
      render: titleContentNode,
      endpoints: [
        {
          id: 'right',
          orientation: [1, 0],
          pos: [0, 0.5]
        }
      ]
    },
    {
      id: 'B',
      isRoot: true,
      title: '数据库B',
      content: '我是数据库B的详细内容',
      render: titleContentNode,
      endpoints: [
        {
          id: 'right',
          orientation: [1, 0],
          pos: [0, 0.5]
        }
      ]
    },
    {
      id: 'C',
      title: '结果1',
      content: '我是结果1的详细内容',
      render: titleContentNode,
      endpoints: [
        {
          id: 'left',
          orientation: [-1, 0],
          pos: [0, 0.5]
        },
        {
          id: 'right',
          orientation: [1, 0],
          pos: [0, 0.5]
        }
      ]
    },
    {
      id: 'D',
      title: '结果2',
      content: '我是结果2的详细内容',
      render: titleContentNode,
      endpoints: [
        {
          id: 'left',
          orientation: [-1, 0],
          pos: [0, 0.5]
        },
        {
          id: 'right',
          orientation: [1, 0],
          pos: [0, 0.5]
        }
      ]
    },
    {
      id: 'E',
      title: '结果3',
      content: '我是结果3的详细内容',
      render: titleContentNode,
      endpoints: [
        {
          id: 'left',
          orientation: [-1, 0],
          pos: [0, 0.5]
        },
        {
          id: 'right',
          orientation: [1, 0],
          pos: [0, 0.5]
        }
      ]
    },
    {
      id: 'F',
      title: '结果4',
      content: '我是结果4的详细内容',
      render: titleContentNode,
      endpoints: [
        {
          id: 'left',
          orientation: [-1, 0],
          pos: [0, 0.5]
        }
      ]
    },
  ],
  edges: [
    {
      id: '1',
      source: 'right',
      target: 'left',
      sourceNode: 'A',
      targetNode: 'C',
      type: 'endpoint',
      Class: Edge
    },
    {
      id: '2',
      source: 'right',
      target: 'left',
      sourceNode: 'B',
      targetNode: 'C',
      type: 'endpoint',
      Class: Edge
    },
    {
      id: '3',
      source: 'right',
      target: 'left',
      sourceNode: 'A',
      targetNode: 'D',
      type: 'endpoint',
      Class: Edge
    },
    {
      id: '4',
      source: 'right',
      target: 'left',
      sourceNode: 'C',
      targetNode: 'D',
      type: 'endpoint',
      Class: Edge
    },
    {
      id: '5',
      source: 'right',
      target: 'left',
      sourceNode: 'D',
      targetNode: 'E',
      type: 'endpoint',
      Class: Edge
    },
    {
      id: '6',
      source: 'right',
      target: 'left',
      sourceNode: 'B',
      targetNode: 'F',
      type: 'endpoint',
      Class: Edge
    },
    {
      id: '7',
      source: 'right',
      target: 'left',
      sourceNode: 'E',
      targetNode: 'F',
      type: 'endpoint',
      Class: Edge
    }
  ]
};

export default data;
