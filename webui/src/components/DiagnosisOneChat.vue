<template>
  <div class="c-flex-column c-relative" style="width: 100%;">
    <div :id="componentId + '-scroll-container'" class="scroll-container c-relative">
      <div
          :class="'message-header rowBC ' + (fold ? 'all-radius' : 'top-radius')"
          :style="'background-color: ' + headerStyles[(sender || 'A').charCodeAt(0) % headerStyles.length]"
      >
        <div>
          <span class="face">
            {{ (sender || 'A').slice(0, 1) }}
          </span>
          <span style="font-size: 16px; color: #FFFFFF; margin-left: 10px">{{ sender || 'A' }}</span>
        </div>
        <div v-if="canFold" style="color: #ffffff; font-size: 20px" @click="toggleFold">
          <el-icon v-show="fold">
            <ArrowDownBold/>
          </el-icon>
          <el-icon v-show="!fold">
            <ArrowUpBold/>
          </el-icon>
        </div>
      </div>
      <template v-if="!fold">
        <div v-for="(item, index) in messageMarkdownDatas" :key="index" class="text-item columnSS">
          <span v-if="item.time" style="font-size: 1rem; color: #666666; margin-bottom: 5px; margin-left: 5px; ">
            {{ item.time }}
          </span>
          <div class="relative content columnSS">
            <div v-html="item.markdownContent"/>
            <div v-if="item.edit" class="footer">
              <el-button type="primary" plain @click="onEditClick(item)">{{ item.type === 'select' ? '选择' : '编辑' }}</el-button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>

import {watch, ref} from 'vue'

import marked from '@/utils/markdownConfig.js'

const props = defineProps({
  messages: {type: Array, default: () => []},
  sender: {required: false, type: String, default: 'A'},
  canFold: {type: Boolean, default: true},
  isFold: {type: Boolean, default: false}
})

const fold = ref(false)

const editIndex = ref(-1)

const headerStyles = ["#01B77E", "#0F2F5F", "#FB9996", "#7649af", "#ecb42b", "#67C23A", "#FFC2E3", "#D51374"]

const componentId = `diagnosis-one-chat-${Math.random().toString(36).slice(2, 11)}`
let scrollObserver = undefined

const messageMarkdownDatas = ref([])

watch(() => props.messages, (newMessages) => {
  messageMarkdownDatas.value = newMessages.map(item => ({
    ...item,
    markdownContent: marked.parse(item.data),
    selectValue: ''
  }))
}, {immediate: true, deep: true})


watch(() => props.isFold, (newVal) => {
  fold.value = newVal
}, {immediate: true})

onBeforeUnmount(() => {
  if (scrollObserver) {
    scrollObserver.disconnect()
    scrollObserver = undefined
  }
})

const emit = defineEmits(['edit-click'])

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

const toggleFold = () => {
  fold.value = !fold.value
}

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
    position: relative;

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

      .footer {
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: flex-end;

        .edit {
          cursor: pointer;
          color: var(--el-color-primary);
        }
      }
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
    background-color: #ffffff;
    text-align: center;
    color: #333333;
    font-size: 24px;
    font-weight: bold;
    box-shadow: 0 0 5px 5px rgba(0, 0, 0, 0.1);
  }
}
</style>

