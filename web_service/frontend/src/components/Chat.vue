<template>
  <div class="c-flex-column c-relative" style="width: 100%; height: 100%;">
    <div id="scroll-container" class="scroll-container c-relative">
      <div v-for="(item, index) in messages" :key="index">
        <div :class="[item.isSelf === 1 ? 'text-item c-flex-row right' : 'text-item c-flex-row left']">
          <template v-if="item.isSelf === 1">
            <img src="@/assets/avatar-user.png" class="face">
          </template>
          <template v-else>
            <img v-if="item.sender === 'RoleAssigner'" src="@/assets/dba_robot.webp" class="face">
            <img v-if="item.sender === 'CpuExpert'" src="@/assets/cpu_robot.webp" class="face">
            <img v-if="item.sender === 'MemoryExpert'" src="@/assets/mem_robot.webp" class="face">
            <img v-if="item.sender === 'IoExpert'" src="@/assets/io_robot.webp" class="face">
            <img v-if="item.sender === 'NetworkExpert'" src="@/assets/net_robot.webp" class="face">
          </template>
          <div v-if="!item.loading" class="c-flex-column">
            <span style="font-size: 12px; color: #333333; margin-bottom: 5px">
              {{ item.sender }}
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
      <div class="item-space" />
    </div>
    <div v-if="false" class="bottom-input-container">
      <el-popover
        v-model="phraseVisible"
        placement="left"
        width="400"
        trigger="hover"
      >
        <div class="c-flex-row c-align-items-center" style="padding: 10px">
          <el-input
            ref="chatInput"
            v-model="chatText"
            style="height: 40px; width: 100%; margin-right: 10px;"
            placeholder="Please enter"
            @keyup.enter.native="onChatConfirm"
          />
          <div
            class="u-text-center"
            style="background: #682FF9; border-radius: 5px; padding: 5px; color: #FFFFFF; flex-shrink: 0; cursor: pointer"
            @click="onChatConfirm()"
          >
            Submit
          </div>
        </div>
        <div
          slot="reference"
          class="c-shaow-card"
          style="background: #682FF9; border-radius: 40px; text-align: center; width: 40px; height: 40px; color: #FFFFFF; flex-shrink: 0;
              font-size: 12px; cursor: pointer; line-height: 40px;"
          @click="phraseVisible=true"
        >
          Chat
        </div>
      </el-popover>
    </div>
  </div>
</template>

<script>
import { parseTime } from '@/utils'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
export default {
  name: 'Chat',
  components: { },
  props: {
    messages: {
      type: Array,
      required: true,
      default: function() {
        return []
      }
    }
  },
  data() {
    return {
      chats: [],
      loading: false,
      openChat: {},
      chatText: '',
      pageNow: 1,
      phraseVisible: false,
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
    },
    onPhraseItemClick(item) {
      this.chatText = item
      this.phraseVisible = false
      if (this.$refs['chatInput']) {
        this.$refs.chatInput.focus()
      }
    },
    onChatConfirm() {
      var text = this.chatText
      if (!text || text.replaceAll(' ', '') === '') {
        this.$onceMessage.info('不能发送空消息')
        return
      }
      this.sentMessage(0, this.chatText)
    },
    sentMessage(type, content) {
      // chatMessageSend({ type: type, content: content, chatID: this.chatID })
      //   .then(res => {
      //     this.hasMore = true
      //     this.chatText = ''
      //     this.getMessages(1, true)
      //   })
      //   .catch(error => {
      //     console.log(error)
      //   })
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

.scroll-container {
  transition: all 0.1s ease;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding-bottom: 20px;
  width: calc(100% - 20px);
  padding-left: 10px;
  padding-right: 10px;
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

  .text-item {
    margin: 20px 0;
    align-items: flex-start;
    justify-content: flex-start;

    .face {
      width: 40px;
      height: 40px;
      border-radius: 40px;
    }

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

    &.left {
      .face {
        margin-right: 7px;
      }
    }

    &.right {
      flex-direction: row-reverse;

      .face {
        margin-left: 7px;
      }

      .content {
        color: #41b584;
        background-color: #ecf8f3;
        border: 1px solid #41b584;
      }
    }
  }
}
</style>

