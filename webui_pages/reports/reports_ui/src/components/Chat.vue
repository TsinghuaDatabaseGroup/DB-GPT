<template>
  <div class="c-flex-column c-relative" style="width: 100%; height: 100%;">
    <div :id="componentId + '-scroll-container'" class="scroll-container c-relative" />
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import Typed from 'typed.js'
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
    },
    skipTyped: {
      type: Boolean,
      default: false
    },
    typeSpeed: {
      type: Number,
      default: 100
    }
  },
  data() {
    return {
      typedObjs: [],
      chatText: '',
      componentId: Math.random().toString(36).substr(2, 9),
      faceMap: {
        'RoleAssigner': require('@/assets/dba_robot.webp'),
        'CpuExpert': require('@/assets/cpu_robot.webp'),
        'MemoryExpert': require('@/assets/mem_robot.webp'),
        'IoExpert': require('@/assets/io_robot.webp'),
        'IndexExpert': require('@/assets/index_robot.webp'),
        'ConfigurationExpert': require('@/assets/configuration_robot.webp'),
        'QueryExpert': require('@/assets/query_robot.webp'),
        'WorkloadExpert': require('@/assets/workload_robot.webp')
      },
      scrollObserver: undefined,
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
  watch: {
    messages: {
      handler() {
        setTimeout(() => {
          this.dealMessage(0)
        })
      },
      deep: true,
      immediate: true
    }
  },
  destroyed() {
    if (this.scrollObserver) {
      this.scrollObserver.disconnect()
      this.scrollObserver = undefined
    }
    this.typedObjs.forEach(item => {
      item.destroy()
    })
  },
  mounted() {
    const target = document.getElementById(this.componentId + '-scroll-container')
    // 创建MutationObserver对象
    this.scrollObserver = new MutationObserver(function() {
      // 处理高度变化操作
      target.scrollTop = target.scrollHeight - target.clientHeight
    })
    // 配置观察选项
    const config = { attributes: true, childList: true, subtree: true }
    // 开始观察目标节点
    this.scrollObserver.observe(target, config)
  },
  methods: {
    dealMessage(index) {
      if (index >= this.messages.length) {
        this.$emit('playbackComplete')
        if (this.scrollObserver) {
          this.scrollObserver.disconnect()
          this.scrollObserver = undefined
        }
        return
      }
      const message = this.messages[index]

      if (!message.data || message.data.trim().length === 0) {
        this.dealMessage(index + 1)
        return
      }

      const faceImage = this.faceMap[message.sender]

      const divId = 'message-' + Math.random().toString(36).substr(2, 9)

      const messagesContainer = document.getElementById(this.componentId + '-scroll-container')
      messagesContainer.innerHTML = messagesContainer.innerHTML +
        `<div class="text-item c-flex-row left">
          <img src="${faceImage}" class="face">
          <div class="c-flex-column">
            <span style="font-size: 1rem; color: #333333; margin-bottom: 5px">
              ${message.sender}
              <span style="margin-left: 5px; color: #666666">${message.time}</span>
            </span>
            <div id="${divId}" class="content c-flex-column"></div>
          </div>
        </div>`
      setTimeout(() => {
        try {
          if (this.skipTyped) {
            const contentContainer = document.getElementById(divId)
            contentContainer.innerHTML = this.md.render(message.data)
            this.dealMessage(index + 1)
          } else {
            const typedObj = new Typed('#' + divId, {
              strings: [this.md.render(message.data)],
              typeSpeed: 100 - this.typeSpeed,
              showCursor: false,
              contentType: 'html',
              onComplete: () => {
                this.dealMessage(index + 1)
              } })
            this.typedObjs.push(typedObj)
          }
        } catch (e) {
          console.log('Typed Error', e)
        }
      }, 0)
    },
    onPhraseItemClick(item) {
      this.chatText = item
      this.phraseVisible = false
      if (this.$refs['chatInput']) {
        this.$refs.chatInput.focus()
      }
    },
    onChatConfirm() {
      const text = this.chatText
      if (!text || text.replaceAll(' ', '') === '') {
        this.$onceMessage.info('不能发送空消息')
      }
    }
  }

}
</script>

<style lang="scss">

.text-item {
  margin: 20px 0;
  align-items: flex-start;
  justify-content: flex-start;

.face {
  width: 40px;
  height: 40px;
  border-radius: 40px;
  margin-right: 7px;
}

.content {
  color: #111111;
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

</style>

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
}
</style>

