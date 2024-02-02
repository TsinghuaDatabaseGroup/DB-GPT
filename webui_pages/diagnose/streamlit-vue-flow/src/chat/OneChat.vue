<template>
  <div style="width: 100%; height: 100%; position: relative; display: flex; flex-direction: column; background: rgb(242, 246, 255)">
    <div class="scroll-container" style="position: relative">
      <div
        class="message-header">
        <span style="font-size: 16px; color: #FFFFFF;">{{ sender }}</span>
      </div>
      <div v-for="(item, index) in chats" :key="index" class="text-item">
            <span style="font-size: 14px; color: #333333; margin-bottom: 5px">
              <span style="margin-left: 5px; color: #666666">{{item.time}}</span>
            </span>
        <div class="report-content" v-html="item.data"></div>
      </div>
    </div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

export default {
  name: 'OneChat',
  components: {},
  props: {
    messages: {
      type: Array,
      required: true,
      default: function() {
        return []
      }
    },
    sender: {
      type: String,
      required: true,
      default: ''
    }
  },
  data() {
    return {
      componentId: Math.random().toString(36).substr(2, 9),
      chats: [],
      scrollObserver: undefined,
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
  watch: {
    messages: {
      handler() {
        console.log('=======:', this.messages)
        this.chats = []
        for (let i = 0; i < this.messages.length; i++) {
          const message = this.messages[i]
          if (!message.data || message.data.trim().length === 0) {
            continue
          }
          this.chats.push({
            time: message.time,
            data: this.md.render(message.data)
          })
        }
      },
      deep: true,
      immediate: true
    }
  }
}
</script>

<style>
.text-item {
  margin: 20px 10px;
  align-items: flex-start;
  justify-content: flex-start;
  word-break: break-all;
  word-wrap: break-word;
  overflow-x: scroll;
  display: flex;
  flex-direction: column;
}

.report-content {
  color: #333333;
  font-size: 14px;
  min-height: 20px;
  border-radius: 20px;
  padding: 6px 12px;
  line-height: 20px;
  background-color: #ffffff;
  word-break: break-all;
  word-wrap: break-word;
  position: relative;
}

.json-viewer {
  width: 100%;
}

details {
  padding: 10px;
  background-color: rgba(23, 95, 255, 0.1);
  border-radius: 8px;
  margin: 10px 0;
}

</style>

<style lang="scss" scoped>

.json-viewer {
  width: 100%;
}

.message-header {
  position: sticky;
  top: 0;
  width: 100%;
  z-index: 10;
  padding: 5px 10px;
  background-color: #7649af;
  text-align: center;
}

.scroll-container {
  transition: all 0.1s ease;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding-bottom: 20px;
  width: 100%;
  height: 100%;
  box-shadow: 0 0 5px 5px rgba(0, 0, 0, 0.1);

  .item-space {
    height: 15px;
  }

  .time {
    color: #666;
    font-size: 12px;
    text-align: center;
    margin-bottom: 10px;
  }

  .time-item {
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    font-size: 15px;
    color: #9d9d9d;
  }

  .face {
    width: 40px;
    height: 40px;
    border-radius: 40px;
    margin-right: 7px;
  }
}
</style>

