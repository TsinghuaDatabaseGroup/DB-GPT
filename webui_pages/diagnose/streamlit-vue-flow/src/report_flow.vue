<template>
  <div class="wrapper" :style="`width: ${ options.width }; height: ${ options.height }; background: ${ options.background };`">
    <butterfly-vue
        ref="butterflyVue"
        :canvasData="nodeData"
        @onLoaded="finishLoaded"
        className='grid'
        key="grid"
    />
  </div>
</template>

<script>
// import { Streamlit } from "streamlit-component-lib";
import {ButterflyVue} from './index.js';
import titleContentNode from './node/title-content-node';
import agentGroupNode from './node/agent_group_node';
import Edge from './util/edge';

const classMap = {
  'titleContentNode': titleContentNode,
  'agentGroupNode': agentGroupNode,
  'Edge': Edge
};

export default {
  name: "ReportFlow",
  props: ["args"],
  components: {
    ButterflyVue
  },
  data() {
    return {
      options: {
        width: '100%',
        height: '300px',
        background: 'rgba(0, 0, 0, 1)',
      },
      runData: {},
      defaults: {
          width: '100%',
          height: '300px',
          background: 'rgba(0, 0, 0, 1)',
      },
      nodeData: {},
      canvansRef:{},
      butterflyVue: {},
      nodeIndex: 0
    };
  },
  watch: {
    args: {
      handler(newVal, oldVal) {
        // Do something when `args` changes
        this.options.width = newVal.args.width || this.defaults.width;
        this.options.height = newVal.args.height  || this.defaults.height;
        this.options.background = newVal.args.background  || this.defaults.background;
        const jsonData = newVal.args.nodeData
        jsonData.nodes.forEach(node => {
          node.render = classMap[node.render];
          node['isDiagnosing'] = jsonData.isDiagnosing;
        });
        jsonData.edges.forEach(edge => {
          edge.Class = classMap[edge.Class];
        });
        this.nodeData = jsonData;
        console.log('Args changed from', oldVal, 'to', newVal);
      },
      deep: true,
      immediate: true
    },
  },
  methods: {
    addEdge() {
      this.mockData.edges.push({
        id: '0-29',
        type: 'node',
        source: '0',
        target: '29',
      })
    },
    finishLoaded(VueCom) {
      this.butterflyVue = VueCom;
      this.canvansRef = VueCom.canvas;
      window.butterflyVue = VueCom;
      console.log("finish:", this.canvansRef);
    },
  }
};
</script>

<style>
.wrapper {
  border-radius: 8px;
  overflow: hidden;
}
</style>
