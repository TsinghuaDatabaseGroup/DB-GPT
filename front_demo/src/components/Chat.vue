<template>
  <div class="c-flex-column c-relative" style="width: 100%; height: 100%; margin-left: 5px">
    <div id="scroll-container" class="scroll-container c-relative">
      <div class="item-space"/>
      <div v-for="(item, index) in messages" :key="index">
        <div :class="[item.isSelf === 1 ? 'text-item c-flex-row right' : 'text-item c-flex-row left']">
          <img v-if="item.isSelf === 1" src="@/assets/avatar-user.png" class="face">
          <img v-else src="@/assets/avatar-robot.png" class="face">
          <div class="content flex-row">{{ item.content }}</div>
        </div>
      </div>
      <div class="item-space"/>
    </div>
    <div class="bottom-input-container">
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

export default {
  name: 'Chat',
  data() {
    return {
      chats: [],
      loading: false,
      messages: [
        { isSelf: 1, content: '测试内容' },
        { isSelf: 0, content: '测试内容11111111111' },
        { isSelf: 1, content: '测试内容' }
      ],
      openChat: {},
      chatText: '',
      pageNow: 1,
      phraseVisible: false,
      refreshInterval: undefined,
      phraseList: [
        '请开始监控',
        '请结束监控',
        '给我一些建议',
        '上面的问题应该怎么解决？'
      ],
      viewPDF: false,
      annexURL: ''
    }
  },
  methods: {
    parseTime(value) {
      return parseTime(value, '{m}-{d}')
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

.chat-item {
  padding: 15px 20px;
  border-bottom: 1px solid #eaeaea;
  margin: 0;
  position: relative;
  cursor: pointer;
}

.chat-table-container {
  overflow: auto;
  width: 20%;
  padding-bottom: 10px;
  height: 100%;
  min-width: 300px;
}

.tag {
  padding: 3px 5px;
  background-color: #f7f7f7;
  border-radius: 2px;
  margin-right: 5px;
  color: #66656c;
  font-size: 11px;
}

.scroll-container {
  transition: all 0.1s ease;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding-bottom: 60px;
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

  .job-item {
    margin: 0 15px 15px;
    align-items: center;
    justify-content: center;
    border-radius: 5px;
    padding: 10px 12px;
    background-color: white;
  }

  .text-item {
    margin: 0 15px 15px;
    align-items: flex-start;
    justify-content: flex-start;

    .face {
      width: 40px;
      height: 40px;
      border-radius: 5px;
    }

    .content {
      color: #111111;
      font-size: 14px;
      min-height: 20px;
      border-radius: 5px;
      padding: 6px 12px;
      background-color: #F2F2F2;
      word-break: break-all;
      word-wrap: break-word;
      max-width: calc(100% - 55px);
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

