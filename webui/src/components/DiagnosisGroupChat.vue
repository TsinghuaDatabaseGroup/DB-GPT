<template>
  <div class="c-flex-column c-relative" style="width: 100%;">
    <div :id="componentId + '-scroll-container'" class="scroll-container c-relative">
      <div v-for="(item, index) in messageMarkdownDatas" :key="index" class="text-item left">
        <div class="rowSC" style="margin-bottom: 10px">
          <div class="face" :style="'background-color: ' + headerStyles[item.sender.charCodeAt(0) % headerStyles.length]">{{ item.sender.slice(0, 1) }}</div>
          <div style="font-size: 1rem; color: #333333; margin-bottom: 5px">
            {{ item.sender }}
            <span style="margin-left: 5px; color: #666666">{{ item.time }}</span>
          </div>
        </div>
        <div class="relative content columnSS">
            <div v-html="item.markdownContent"/>
            <div v-if="item.edit" class="footer">
              <el-button type="primary" plain @click="onEditClick(item)">{{ item.type === 'select' ? '选择' : '编辑' }}</el-button>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import marked from '@/utils/markdownConfig.js'

const headerStyles = ["#01B77E", "#0F2F5F", "#FB9996", "#7649af", "#ecb42b", "#67C23A", "#FFC2E3", "#D51374"]

const props = defineProps({
  messages: {type: Array, default: () => []}
})

const emit = defineEmits(['edit-click'])

const componentId = `diagnosis-chat-${Math.random().toString(36).slice(2, 11)}`
let scrollObserver = undefined

const messageMarkdownDatas = computed(() => {
  return props.messages.map(item => {
    return {
      ...item,
      markdownContent: marked.parse(item.data)
    }
  })
})

onBeforeUnmount(() => {
  if (scrollObserver) {
    scrollObserver.disconnect()
    scrollObserver = undefined
  }
})

onMounted(() => {
  const target = document.querySelector(`#${componentId}-scroll-container`)
  if (target) {
    scrollObserver = new MutationObserver((mutationsList, observer) => {
      target.scrollTop = target.scrollHeight - target.clientHeight
    })
    const config = {attributes: true, childList: true, subtree: true}
    if (scrollObserver) { //检查scrollObserver是否存在
      scrollObserver.observe(target, config)
    } else {
      console.error('scrollObserver is undefined')
    }
  } else {
    console.error('Element is not mounted yet')
  }
})

const onEditClick = (item) => {
  emit('edit-click', item)
}

</script>

<style>


</style>

<style lang="scss" scoped>

.top-radius {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.all-radius {
  border-radius: 8px;
}

.scroll-container {
  transition: all 0.1s ease;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding-bottom: 20px;
  width: 100%;
  background: #ffffff;
  border-radius: 8px;

  .message-header {
    position: sticky;
    top: 0;
    width: 100%;
    z-index: 10;
    padding: 5px 10px;
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
      border-radius: 8px;
      padding: 6px 12px;
      line-height: 20px;
      background-color: #f4f4f4;
      word-break: break-all;
      word-wrap: break-word;
      position: relative;
    }

  }

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
    line-height: 40px;
    border-radius: 40px;
    margin-right: 7px;
    text-align: center;
    color: #ffffff;
    font-size: 24px;
    font-weight: bold;
  }
}
</style>

