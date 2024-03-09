const position = { x: 0, y: 0 }
const nodeType = 'process'
const edgeType = ''

export const initialNodes = [
  {
    id: '0',
    position,
    type: nodeType,
    data: {
      type: 'db'
    }
  },
  {
    id: '1',
    position,
    type: nodeType,
    data: {
      type: 'file'
    }
  },
  {
    id: '2',
    position,
    type: nodeType,
    data: {
      type: 'message'
    }
  },
  {
    id: '3',
    position,
    type: nodeType,
    data: {
      type: 'message'
    }
  },
  {
    id: '4',
    position,
    type: nodeType,
    data: {
      type: 'message'
    }
  },
  {
    id: '5',
    position,
    type: nodeType,
    data: {
      type: 'message'
    }
  },
  {
    id: '7',
    position,
    type: nodeType,
    data: {
      type: 'message'
    }
  },
]

export const initialEdges = [
  { id: 'e1-1', source: '0', target: '2', type: edgeType, animated: true },
  { id: 'e3-7', source: '0', target: '4', type: edgeType, animated: true },
  { id: 'e1-3', source: '0', target: '3', type: edgeType, animated: true },
  { id: 'e1-3', source: '2', target: '7', type: edgeType, animated: true },
  { id: 'e1-2', source: '1', target: '2', type: edgeType, animated: true },
  { id: 'e1-4', source: '1', target: '2', type: edgeType, animated: true },
  { id: 'e4-5', source: '1', target: '5', type: edgeType, animated: true },
  { id: 'e5-7', source: '5', target: '7', type: edgeType, animated: true },
  { id: 'e5-7', source: '1', target: '7', type: edgeType, animated: true },
]
