<template>
  <div class="c-flex-column c-relative" style="width: 100%; height: 100%;">
    <div :id="componentId + '-scroll-container'" class="scroll-container c-relative">
      <div
        class="message-header c-relative c-flex-row c-align-items-center"
        :style="headerStyle[sender]"
      >
        <img v-if="sender === 'RoleAssigner'" src="@/assets/dba_robot.webp" class="face"/>
        <img v-if="sender === 'CpuExpert'" src="@/assets/cpu_robot.webp" class="face"/>
        <img v-if="sender === 'MemoryExpert'" src="@/assets/mem_robot.webp" class="face"/>
        <img v-if="sender === 'IoExpert'" src="@/assets/io_robot.webp" class="face"/>
        <img v-if="sender === 'IndexExpert'" src="@/assets/index_robot.webp" class="face"/>
        <img v-if="sender === 'ConfigurationExpert'" src="@/assets/configuration_robot.webp" class="face"/>
        <img v-if="sender === 'QueryExpert'" src="@/assets/query_robot.webp" class="face"/>
        <img v-if="sender === 'WorkloadExpert'" src="@/assets/workload_robot.webp" class="face"/>
        <span style="font-size: 16px; color: #FFFFFF; margin-left: 10px">{{ sender }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>

import marked from '@/utils/markdownConfig.js'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  sender: { required: true, type: String },
  skipTyped: { type: Boolean, default: false },
  typeSpeed: { type: Number, default: 100 }
})

const emit = defineEmits(['playback-complete'])

const headerStyle = {
  'RoleAssigner': 'background-color: #01B77E;',
  'CpuExpert': 'background-color: #0F2F5F;',
  'MemoryExpert': 'background-color: #FB9996;',
  'IoExpert': 'background-color: #7649af;',
  'IndexExpert': 'background-color: #ecb42b;',
  'ConfigurationExpert': 'background-color: #67C23A;',
  'QueryExpert': 'background-color: #FFC2E3;',
  'WorkloadExpert': 'background-color: #D51374;'
};
const typedObjs = ref([])
const componentId = `report-one-chat-${Math.random().toString(36).slice(2, 11)}`
const chats = ref([])
let scrollObserver = undefined
// watch props changes
watch(() => props.messages, (newVal, oldVal) => {
  setTimeout(() => {
    if (props.messages.length > 0) {
      dealMessage(0)
    }
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

const dealMessage = async (index) => {
  if (index >= props.messages.length) {
    emit('playback-complete');
    if (scrollObserver) {
      scrollObserver.disconnect();
      scrollObserver = undefined;
    }
    return;
  }

  const message = props.messages[index];

  if (!(message.data && message.data.trim())) {
    dealMessage(index + 1);
    return;
  }

  const divId = `message-${  Math.random().toString(36).slice(2, 11)}`;

  const messagesContainer = document.querySelector(`#${componentId}-scroll-container`);
  messagesContainer.innerHTML = `${messagesContainer.innerHTML
  }<div class="text-item c-flex-column">
          <span style="font-size: 1rem; color: #333333; margin-bottom: 5px">
            <span style="margin-left: 5px; color: #666666">${message.time}</span>
          </span>
          <div id="${divId}" class="content c-flex-column"></div>
      </div>`;

  await nextTick();

  try {
    if (props.skipTyped) {
      const contentContainer = document.querySelector(`#${divId}`);
      contentContainer.innerHTML = marked.parse(message.data);
      dealMessage(index + 1);
    } else {
      const typedObj = new Typed(`#${  divId}`, {
        strings: [marked.parse(message.data)],
        typeSpeed: 100 - props.typeSpeed,
        showCursor: false,
        contentType: 'html',
        onComplete: () => {
          dealMessage(index + 1);
        }
      });
      typedObjs.value.push(typedObj);
    }
  } catch (e) {
    console.log('Typed Error', e);
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

.json-viewer {
  width: 100%;
}

</style>

<style lang="scss" scoped>

.json-viewer {
  width: 100%;
}

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

