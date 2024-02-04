<template>
  <div class="node">
    <div class="header" :style="itemData.userData.isCompleted ? 'background-color: RGBA(103, 194, 58, 0.9);': 'background-color: #3C3A3A;'">
      {{itemData.userData.title}}
    </div>
    <template v-if="!itemData.userData.isCompleted">
      <div class="content">
        {{itemData.userData.content}}
      </div>
    </template>
    <template v-else>
      <el-popover
          placement="top-start"
          title=""
          trigger="hover"
      >
        <div
            style="width: auto; height: 800px; border-radius: 8px; overflow-y: scroll; overflow-x: scroll;
             z-index: 9999999999; background-color: RGBA(242, 246, 255, 1); padding: 20px">
          <div style="transform: scale(0.8); width: 100%; height: 100%" v-html="report"></div>
        </div>
        <div slot="reference" class="content">
          {{itemData.userData.content}}
        </div>
      </el-popover>
    </template>
    <div v-if="itemData.userData.isRuning" class="blinking-dot"></div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
export default {
  name: "title-content-node",
  props: {
    itemData: {
      type: Object,
    },
    canvasNode: {
      type: Object
    }
  },
  watch: {
    itemData: {
      handler: function (val) {
        const report = val.userData.messages;
        if (!report || report.trim().length === 0) {
          this.report = '';
        }else {
          this.report = this.md.render(report);
        }
      },
      deep: true,
      immediate: true
    }
  },
  data() {
    return {
      report: '',
      md: new MarkdownIt()
          .set({ html: true, breaks: true, typographer: true, linkify: true })
          .set({
            highlight: function(code) {
              return '<pre class="hljs"><code>' +
                  hljs.highlight(code, { language: 'python', ignoreIllegals: true }).value +
                  '</code></pre>'
            }
          })
    }
  },
  components: {
  },
  methods: {}
};
</script>

<style>

.node {
  width: 240px;
  box-shadow: 0 2px 3px 0 rgba(0,112,204,0.06);;
  border-radius:8px;
  overflow: hidden;
  position: relative;
}

.header {
  position: relative;
  padding: 5px 20px;
  border-radius: 5px 5px 0 0;
  color: #FFF;
  border: none;
  min-height: 10px;
  background-color: #3C3A3A;
  text-align: center;
  font-size: 14px;
}

.content {
  position: relative;
  color: #ffffff;
  padding: 10px;
  border-top: 2px solid #000000;
  border-radius: 0 0 5px 5px;
  min-height: 60px;
  font-size: 12px;
  background-color: #3C3A3A;
  word-break: break-all;
  height: 60px;
  text-overflow: ellipsis;
  overflow: hidden;
}

</style>
