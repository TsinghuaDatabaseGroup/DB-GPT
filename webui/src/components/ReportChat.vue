<template>
  <div class="c-flex-column c-relative" style="width: 100%; height: 100%;">
    <div :id="componentId + '-scroll-container'" class="scroll-container c-relative" />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { Marked } from "marked";
import { markedHighlight } from "marked-highlight";
import "highlight.js/styles/gruvbox-dark.css";
import hljs from 'highlight.js';
import Typed from 'typed.js'

const marked = new Marked(
    markedHighlight({
      langPrefix: 'hljs language-',
      highlight(code, lang, info) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
      }
    })
);

const props = defineProps({
  messages: { type: Array, default: () => [] },
  skipTyped: { type: Boolean, default: false },
  typeSpeed: { type: Number, default: 100 }
})

const emit = defineEmits(['playback-complete'])

const typedObjs = ref([])
const componentId = `report-chat-${Math.random().toString(36).slice(2, 11)}`
const faceMap = {
  'RoleAssigner': new URL('../assets/dba_robot.webp', import.meta.url).href,
  'CpuExpert': new URL('../assets/cpu_robot.webp', import.meta.url).href,
  'MemoryExpert': new URL('../assets/mem_robot.webp', import.meta.url).href,
  'IoExpert': new URL('../assets/io_robot.webp', import.meta.url).href,
  'IndexExpert': new URL('../assets/index_robot.webp', import.meta.url).href,
  'ConfigurationExpert': new URL('../assets/configuration_robot.webp', import.meta.url).href,
  'QueryExpert': new URL('../assets/query_robot.webp', import.meta.url).href,
  'WorkloadExpert': new URL('../assets/workload_robot.webp', import.meta.url).href
}
let scrollObserver = undefined

// watch props changes
watch(() => props.messages, (newVal, oldVal) => {
  setTimeout(() => {
    dealMessage(0)
  })
}, { deep: true, immediate: true })

onBeforeUnmount(() => {
  if (scrollObserver) {
    scrollObserver.disconnect()
    scrollObserver = undefined
  }
  typedObjs.value.forEach(item => {
    item.destroy()
  })
})

onMounted(() => {
  const target = document.querySelector(`#${componentId}-scroll-container`)
  if (target) {
    scrollObserver = new MutationObserver((mutationsList, observer) => {
      target.scrollTop = target.scrollHeight - target.clientHeight
    })
    const config = { attributes: true, childList: true, subtree: true }

    if(scrollObserver){ //检查scrollObserver是否存在
      scrollObserver.observe(target, config)
    } else {
      console.error('scrollObserver is undefined')
    }
  } else {
    console.error('Element is not mounted yet')
  }
})

const dealMessage = (index) => {
  if (index >= props.messages.length) {
    emit('playback-complete')
    if (scrollObserver) {
      scrollObserver.disconnect()
      scrollObserver = undefined
    }
    return
  }
  const message = props.messages[index]

  if (!message.data || message.data.trim().length === 0) {
    dealMessage(index + 1)
    return
  }

  const faceImage = faceMap[message.sender]

  const divId = `message-${  Math.random().toString(36).slice(2, 11)}`

  const messagesContainer = document.querySelector(`#${componentId}-scroll-container`);
  messagesContainer.innerHTML = `${messagesContainer.innerHTML
  }<div class="text-item c-flex-row left">
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
      if (props.skipTyped) {
        const contentContainer = document.querySelector(`#${divId}`);
        contentContainer.innerHTML = marked.parse(message.data)
        dealMessage(index + 1)
      } else {
        const typedObj = new Typed(`#${  divId}`, {
          strings: [marked.parse(message.data)],
          typeSpeed: 100 - props.typeSpeed,
          showCursor: false,
          contentType: 'html',
          onComplete: (self) => {
            dealMessage(index + 1)
          } })
        typedObjs.value.push(typedObj)
      }
    } catch (e) {
      console.log('Typed Error', e)
    }
  }, 0)
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

