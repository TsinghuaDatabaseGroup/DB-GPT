<template>
  <div class="relative columnSC diagnose-container">
    <div class="header">
      <el-upload
          :class="diagnoseStatus ? 'upload upload-disabled' : 'upload'"
          drag
          action=""
          :disabled="diagnoseStatus"
          accept=".json,.jsonl"
          :http-request="uploadFile"
      >
        <el-icon class="el-icon--upload">
          <upload-filled/>
        </el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            json/jsonl files with a size less than 20MB
          </div>
        </template>
      </el-upload>
    </div>
    <div ref="messagesScrollDiv" class="diagnose-messages-container">
      <div class="output" style="white-space: pre-wrap; word-break: break-all" v-html="diagnoseOutputHtml"/>
      <div v-if="diagnoseStatus" style="position: fixed; right: 30px; bottom: 100px">
        <el-icon class="is-loading" size="26" style="color: limegreen; font-weight: bold">
          <Loading/>
        </el-icon>
      </div>
    </div>
    <BottomInputContainer style="width: calc(100% - 20px)" placeholder="Ask anything" @send-click="onSendClick">
      <template v-if="diagnoseStatus" #right>
        <div style="margin-left: 10px; cursor: pointer" @click="onStopDiagnoseClick">
          <svg t="1709818874544" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4540" width="32" height="32">
            <path
                d="M512 1024a512 512 0 1 1 512-512 512 512 0 0 1-512 512z m0-896a384 384 0 1 0 384 384A384 384 0 0 0 512 128z m128 576h-256a64 64 0 0 1-64-64v-256a64 64 0 0 1 64-64h256a64 64 0 0 1 64 64v256a64 64 0 0 1-64 64z"
                fill="#d81e06" p-id="4541"/>
          </svg>
        </div>
      </template>
    </BottomInputContainer>
  </div>
</template>

<script setup lang="ts" name="Index">

import {diagnoseOutputReq, diagnoseStatusReq, diagnoseStopDiagnoseReq, diagnoseUserFeedbackReq, runDiagnoseReq} from "@/api/diagnose.js";
import BottomInputContainer from "@/components/BottomInputContainer.vue";
import marked from '@/utils/markdownConfig.js'
import {ElMessage, ElMessageBox} from "element-plus";
import {ref} from 'vue'

const router = useRouter()

const diagnoseOutput: Ref<string> = ref('')

const diagnoseStatus: Ref<Boolean> = ref(false)

const messagesScrollDiv = ref<HTMLElement | null>(null);

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
  })
});

const getDiagnoseStatus = async () => {
  diagnoseStatusReq().then(res => {
    diagnoseStatus.value = res.data.is_alive;
    if (diagnoseStatus.value) {
      setTimeout(() => {
        getDiagnoseStatus()
      }, 5000)
    }
  }).finally(() => {
    getDiagnoseOutput()
  })
}

const getDiagnoseOutput = async () => {
  diagnoseOutputReq().then(res => {
    diagnoseOutput.value = res.data.output;
  })
}

const uploadFile = (files) => {
  runDiagnoseReq(files.file).then(() => {
    ElMessage({
      type: 'success',
      message: 'Upload Successfully!',
    })
    getDiagnoseStatus()
  }).finally(() => {

  })
}

const onSendClick = (value) => {
  if (value === '') {
    ElMessage.error('Please input something')
    return
  }
  diagnoseOutput.value += `\nUser: ${value}`
  diagnoseUserFeedbackReq(value).then(() => {
    ElMessage({
      type: 'success',
      message: 'Feedback Successfully!',
    })
  }).finally(() => {
  })
}

const onStopDiagnoseClick = () => {

  ElMessageBox.confirm(
      'Will stop diagnose. Continue?',
      'Warning',
      {
        confirmButtonText: 'Stop',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
  )
      .then(() => {
        diagnoseStopDiagnoseReq().then(() => {
          ElMessage({
            type: 'success',
            message: 'Stop Successfully!',
          })
        }).finally(() => {
          getDiagnoseStatus()
        })
      }).catch(() => {})
}

</script>

<style lang="scss">
.el-upload {
  --el-upload-dragger-padding-horizontal: 0px !important;
}

.el-upload-dragger {
  border: none;
  background: transparent;;
}

.output {
  font-size: 14px;
  color: #ffffff;
  white-space: pre-wrap;
  word-break: break-all;

  h1, h2, h3, h4, h5, h6 {
    font-size: 14px;
    color: #ffffff;
  }
}
</style>

<style lang="scss" scoped>
.diagnose-container {
  height: calc(100vh - 40px);
  overflow: hidden;

  .header {
    width: 100%;

    .upload-disabled {
      background: #e2e2e2;
    }

    .upload {
      width: 100%;
      border: 2px dashed var(--el-color-primary);
      border-radius: 15px;

      .el-icon--upload {
        font-size: 30px;
        color: var(--el-color-primary);
        margin-bottom: 0 !important;
        line-height: 1;
      }

      .el-upload__text {
        font-size: 14px;
        color: var(--el-color-primary);

        em {
          color: var(--el-color-primary);
          font-style: normal;
        }
      }

      .el-upload__tip {
        font-size: 12px;
        color: #333333;
        width: 100%;
        text-align: center;
      }
    }
  }

  .diagnose-messages-container {
    position: relative;
    height: calc(100vh - 110px);
    width: calc(100% - 20px);
    flex-shrink: 1;
    color: #ffffff;
    background: RGBA(8, 1, 30, 1.00);
    overflow-y: auto;
    padding: 20px;
    border-radius: 10px;
    margin: 10px;
  }
}
</style>
