<template>
  <div class="c-flex-column c-relative" style="width: 100%; height: 100%;">
    <div id="scroll-container" class="scroll-container c-relative">
      <div
        class="message-header c-relative c-flex-row c-align-items-center"
        :style="hire ? 'background-color: #67C23A;' : 'background-color: RGBA(225, 243, 216, 1.00);'"
      >
        <img v-if="sender === 'RoleAssigner'" src="@/assets/dba_robot.webp" class="face">
        <img v-if="sender === 'CpuExpert'" src="@/assets/cpu_robot.webp" class="face">
        <img v-if="sender === 'MemoryExpert'" src="@/assets/mem_robot.webp" class="face">
        <img v-if="sender === 'IoExpert'" src="@/assets/io_robot.webp" class="face">
        <img v-if="sender === 'NetworkExpert'" src="@/assets/net_robot.webp" class="face">
        <span style="font-size: 16px; color: #FFFFFF; margin-left: 10px">{{ sender }}</span>
      </div>
      <template v-if="hire">
        <div v-for="(item, index) in messages" :key="index">
          <div class="text-item c-flex-row left">
            <div v-if="!item.loading" class="c-flex-column">
              <span style="font-size: 12px; color: #333333; margin-bottom: 5px">
                <span style="margin-left: 5px; color: #666666">{{ item.time }}</span>
              </span>
              <div class="content c-flex-column">
                <div v-html="md.render(item.data)" />
              </div>
            </div>
            <div v-else>
              <div class="content c-flex-row c-justify-content-left" style="padding: 10px 40px 10px 20px">
                <i class="el-icon-loading" style="font-size: 20px; color: #000000" />
              </div>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="c-flex-column c-align-items-center c-justify-content-center" style="height: 60%;">
          <span style="font-size: 14px; color: #999999;">未被雇佣</span>
        </div>
      </template>
      <div class="item-space" />
    </div>
  </div>
</template>

<script>
import { parseTime } from '@/utils'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
export default {
  name: 'OneChat',
  components: { },
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
    },
    hire: {
      type: Boolean,
      required: true,
      default: false
    }
  },
  data() {
    return {
      chats: [],
      md: new MarkdownIt()
        .set({ html: true, breaks: true, typographer: true, linkify: true })
        .set({ highlight: function(code) {
          return '<pre class="hljs"><code>' +
              hljs.highlight(code, { language: 'python', ignoreIllegals: true }).value +
              '</code></pre>'
        } })
    }
  },
  methods: {
    parseTime(value) {
      return parseTime(value, '{m}-{d}')
    },
    isNotEmpty(arr) {
      return arr && arr.length > 0 && arr.some(element => element.trim() !== '')
    },
    // 初始化滚动
    initScrollBar() {
      this.$nextTick(() => {
        var container = this.$el.querySelector('.scroll-container')
        container.scrollTop = container.scrollHeight
      })
    }
  }
}
</script>

<style lang="scss" scoped>

.bottom-input-container {
  background: #ffffff;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  position: absolute;
}

.message-header {
  position: sticky;
  top: 0;
  width: 100%;
  background-color: #67C23A;
  z-index: 10;
  padding: 5px 10px
}

.scroll-container {
  transition: all 0.1s ease;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding-bottom: 20px;
  width: 100%;
  height: 100%;

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

  .text-item {
    margin: 20px 10px;
    align-items: flex-start;
    justify-content: flex-start;
    word-break: break-all;
    word-wrap: break-word;
    overflow-x: scroll;
    .content {
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
  }
}
</style>

