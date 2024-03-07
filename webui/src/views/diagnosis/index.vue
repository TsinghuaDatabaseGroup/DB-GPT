<template>
  <div class="relative columnSC diagnose-container">
    <div ref="messagesScrollDiv" class="diagnose-messages-container">
      <div style="white-space: pre-wrap" v-html="diagnoseOutputHtml" />
    </div>
    <BottomInputContainer style="width: calc(100% - 20px)" placeholder="Ask anything" @send-click="onSendClick" />
  </div>
</template>

<script setup lang="ts" name="Index">

import {diagnoseStatusReq, diagnoseOutputReq} from "@/api/diagnose.js";
import {ElMessage} from "element-plus";
import BottomInputContainer from "@/components/BottomInputContainer.vue";
import { reactive, ref } from 'vue'
import marked from '@/utils/markdownConfig.js'

const CHAT_HISTORY_KEY = 'dbgpt-chat-history'

const router = useRouter()

const diagnoseOutput: Ref<string> = ref('')

const diagnoseStatus: Ref<Boolean> = ref(false)

const messagesScrollDiv  = ref<HTMLElement | null>(null);

const diagnoseOutputHtml = computed(() => {
  return marked.parse(diagnoseOutput.value)
})

watch(() => diagnoseOutput.value, () => {
  nextTick(() => {
    if (messagesScrollDiv.value) {
      messagesScrollDiv.value.scrollTop = messagesScrollDiv.value.scrollHeight;
    }
  })
})

onMounted(() => {
  nextTick(() => {
    getDiagnoseStatus()
    getDiagnoseOutput()
  })
});

const getDiagnoseStatus = async () => {
  diagnoseStatusReq().then(res => {
    diagnoseStatus.value = res.data.is_alive;
  })
}

const getDiagnoseOutput = async () => {
  diagnoseOutputReq().then(res => {
    diagnoseOutput.value = res.data.output;
    console.log('===res==:', diagnoseOutput.value)
  })
}

const addUserMessage = (content: string) => {
  const userMessage: Message = {
    role: 'user',
    content,
    time: moment().format('YYYY-MM-DD HH:mm:ss'),
    loading: false
  }
  messageList.value.push(userMessage)
}

const addRobotMessage = (content: string) => {
  const robotMessage: Message = {
    role: 'assistant',
    content,
    time: moment().format('YYYY-MM-DD HH:mm:ss'),
    loading: true
  }
  messageList.value.push(robotMessage)
}

const updateLastRobotMessage = (content: string) => {
  const lastMessageIndex = messageList.value.length - 1;
  const lastMessage = messageList.value[lastMessageIndex];
  const updatedMessage = {
    ...lastMessage,
    content,
    loading:false
  };
  messageList.value[lastMessageIndex] = updatedMessage;
}

const updateLastRobotMessageLoading = (loading: boolean) => {
  const lastMessage = messageList.value[messageList.value.length - 1]
  lastMessage.loading = loading
}

const getHistoryMessages = () => {
  return messageList.value.slice(-historyLength.value).map(item => {
    return {
      role: item.role,
      content: item.content
    }
  })
}

const saveHistoryMessagesToLocal = () => {
  localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messageList.value))
}

const getLocalHistoryMessages = () => {
  const historyMessages = JSON.parse(localStorage.getItem(CHAT_HISTORY_KEY) || '[]')
  return historyMessages.map((item: Message) => {
    return {
      role: item.role,
      content: item.content,
      time: item.time,
      loading: item.loading
    };
  });
}

const onSendClick = (value) => {
  if (value === '') {
    ElMessage.error('Please input something')
    return
  }
  const userInputValue = value
  const historyMessages = getHistoryMessages() || []
  addUserMessage(userInputValue)
  saveHistoryMessagesToLocal()
  addRobotMessage('')
  saveHistoryMessagesToLocal()
  chatReq(userInputValue,"",llmModel.value,historyMessages,historyLength.value).then(res => {
    console.log(res)
    updateLastRobotMessage(res.text)
  }).finally(() => {
    updateLastRobotMessageLoading(false)
    saveHistoryMessagesToLocal()
  })
}

</script>

<style>
.llm-select .el-select__wrapper {
  background-color: transparent!important;
  box-shadow: None!important;
}
</style>


<style lang="scss" scoped>
.diagnose-container {
  height: calc(100vh - 40px);
  overflow: hidden;
  .header {
    width: 100%;
    border-bottom: 1px solid #eeeeee;
    display: flex;
    align-items: center;
    padding: 10px 20px;
    flex-wrap: wrap;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    grid-gap: 10px 20px;
  }
  .diagnose-messages-container {
    height: calc(100vh - 160px);
    width: 100%;
    flex-shrink: 1;
    background: transparent;
    overflow-y: auto;
    padding: 20px;
  }
}
</style>
