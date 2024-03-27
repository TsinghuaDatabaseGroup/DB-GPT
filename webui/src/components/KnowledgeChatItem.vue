<template>
  <div class="chat-item-container">
    <div :class="'rowSC ' + roleClass">
      <img v-if="isUser" src="@/assets/chat-user.png" class="face"/>
      <img v-else src="@/assets/chat-robot.png" class="face" />
      <!--      <span style="margin: 0 10px; color: red">abc</span>-->
      <!--      <span style="color: #2c59cb">sdada</span>-->
      <el-button v-if="isLast && message.cache" size="small" type="primary" plain style="margin-left: 10px; margin-top: 4px" @click="onIgnoreMessageCacheClick">
        <el-icon style="margin-right: 6px" size="16"><MostlyCloudy /></el-icon>{{ $t('IgnoreMessageCache') }}
      </el-button>
    </div>
    <div :class="'rowSC ' + roleClass">
      <div v-if="!message.loading">
        <div class="columnSS content">
          <template v-if="!message.cache">
            <div v-html="htmlContent" />
            <div v-if="message.docsDetail.length > 0" class="rowSC" style="width: 100%; margin-bottom: 10px">
              <div class="rowSC" style="color: #888888; font-weight: bold; margin-right: 10px">
                <img src="@/assets/knowledge_ chat_quote.png" style="width: 20px; margin-right: 10px" />
                {{ $t('ReferenceTitle') }}
              </div>
              <div style="height: 1.5px; flex: 1 1 0; background: #eeeeee" />
            </div>
            <div v-for="(item, index) in message.docsDetail" :key="index" class="rowSC quote-item" @click="onQuoteClick(item)">
              <el-icon style="margin-left: 6px; margin-right: 6px" size="12" color="#06a411"><Document /></el-icon>
              <div style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; font-size: 12px!important;">
                {{ item.filename }}
                <el-tag size="small" style="margin-left: 5px; font-size: 11px!important;">{{item.contents.length}} paragraphs</el-tag>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="columnSS">
              <div class="rowSC" style="margin: 10px 0; color: var(--el-color-success); font-size: 14px; font-weight: bold">
                <el-icon size="18" style="margin-right: 6px;"><Clock /></el-icon>
                历史答案的缓存命中：
              </div>
              <div v-for="(item, index) in message.cacheData" :key="index" class="columnSS" style="width: 100%; margin-bottom: 10px">
                <div style="color: var(--el-color-primary); line-height: 1.2; margin-bottom: 10px">ASK：{{ item.page_content }}</div>
                <span style="color: #666666; line-height: 1.4; white-space: pre-line;">Answer：{{ item.answer }}</span>
              </div>
            </div>
          </template>
        </div>
      </div>
      <div v-else>
        <div class="content rowBC" style="padding: 10px 20px">
          <el-icon class="is-loading" size="20" color="#333333">
            <Loading />
          </el-icon>
        </div>
      </div>
    </div>
    <el-dialog v-model="quoteDialogVisible" class="quote-dialog" :show-close="true" width="60%">
      <template #header>
        <div class="quote-dialog-header">
          <el-tooltip
              class="box-item"
              effect="dark"
              content="Click to download"
              placement="bottom-start"
          >
            <div @click="navigateTo(currentQuoteItem.url)">{{currentQuoteItem.filename}}</div>
          </el-tooltip>
        </div>
      </template>
      <div class="columnSS">
        <div v-for="(item, index) in currentQuoteItem.contents" :key="index" class="columnSS quote-dialog-content-item">
          <div class="rowSC" style="color: #06a411; font-size: 14px; margin-bottom: 8px;">
            <span style="margin-right: 10px; border: 1px solid #06a411; border-radius: 6px; padding: 2px 5px">#{{index + 1}}</span>
            <svg
t="1708530334824" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="15983" width="14"
                 height="14">
              <path
fill="#333333"
                    d="M854.013267 0.001792A170.751402 170.751402 0 0 1 1023.996672 170.753194v682.493612A170.751402 170.751402 0 0 1 854.013267 1023.998208H171.263657A170.495403 170.495403 0 0 1 0.000256 853.246806V170.753194A170.495403 170.495403 0 0 1 171.263657 0.001792zM363.006985 835.070869a15.615945 15.615945 0 0 0-15.615945 15.615946v13.823951a15.359946 15.359946 0 0 0 4.863983 11.263961 14.847948 14.847948 0 0 0 11.51996 4.351985l82.68771-3.839987c27.903902 0 51.199821-1.535995 68.095762-1.535995 25.59991 0 70.143754 1.535995 136.959521 4.607984h22.015923a15.615945 15.615945 0 0 0 15.615945-15.615945v-14.079951a15.615945 15.615945 0 0 0-15.615945-15.615945h-2.303992a143.103499 143.103499 0 0 1-45.82384-5.63198 42.495851 42.495851 0 0 1-24.063916-18.431936 127.999552 127.999552 0 0 1-9.727966-40.191859C588.798195 752.639158 588.798195 721.407267 588.798195 676.351425v-95.487666c0-46.591837 0-108.031622 2.559991-329.214848a15.615945 15.615945 0 0 1 15.615946-15.615945h74.23974c51.199821 0 87.039695 7.167975 104.703633 21.759924a153.599462 153.599462 0 0 1 31.48789 70.399753 15.871944 15.871944 0 0 0 17.663938 11.263961l16.895941-2.559991a15.615945 15.615945 0 0 0 13.055954-17.407939 1800.953697 1800.953697 0 0 1-7.935972-75.007738 981.500565 981.500565 0 0 1-3.327988-82.431711 12.543956 12.543956 0 0 0-4.863983-8.447971 12.287957 12.287957 0 0 0-10.495963-2.559991 236.799171 236.799171 0 0 1-39.167863 6.143979c-25.59991 2.047993-68.351761 2.81599-131.071542 2.81599h-307.198924c-55.807805 0-95.487666 0-119.039584-2.81599a278.527025 278.527025 0 0 1-36.863871-5.375981 15.103947 15.103947 0 0 0-12.799955 2.81599 16.639942 16.639942 0 0 0-6.143978 11.519959c-2.047993 31.231891-4.351985 55.551806-6.655977 72.703746s-7.423974 45.311841-14.847948 81.407715a15.871944 15.871944 0 0 0 14.591949 17.663938l18.687934 3.839987a15.615945 15.615945 0 0 0 18.175937-10.495963 161.535435 161.535435 0 0 1 35.327876-72.703746c19.711931-15.103947 56.319803-22.527921 109.823616-22.527921h71.935748a15.871944 15.871944 0 0 1 11.007961 4.607984 15.359946 15.359946 0 0 1 4.607984 11.007961v276.223033c0 99.327652 0 167.423414-2.047993 204.799284a291.838979 291.838979 0 0 1-7.167974 69.375757 45.311841 45.311841 0 0 1-23.295919 25.59991 126.463557 126.463557 0 0 1-51.199821 7.423974z m0 0" p-id="15984"/></svg>
            <span style="margin-left: 5px; color: #666666">{{item.length}}</span>
          </div>
          <div style="font-size: 14px!important; margin-bottom: 10px">
            {{ item }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">

import marked from '@/utils/markdownConfig.js'

const props = defineProps({
  message: {required:true, type: Object, default: null },
  isLast: {required:true, type: Boolean, default: false }
})

const isUser = computed(() => props.message.role === 'user')

const roleClass = computed(() => props.message.role === 'user' ? 'right' : 'left')

const emit = defineEmits(['ignore-message-cache'])

const htmlContent = computed(() => {
  return marked.parse(props.message.content)
})

const currentQuoteItem = ref({})

const quoteDialogVisible = ref(false)

const onQuoteClick = (item: object) => {
  currentQuoteItem.value = item
  quoteDialogVisible.value = true
}

const onIgnoreMessageCacheClick = () => {
  emit('ignore-message-cache', props.message)
}

const navigateTo = (url: string) => {
  window.location.href = url;
}

</script>

<style>
.hljs {
  border-radius: 8px!important;
  padding: 10px!important;
}
.quote-dialog .el-dialog__body {
  padding: 10px 20px;
}
</style>

<style lang="scss">

.chat-item-container {
  margin: 5px 0;
  display: flex;
  flex-direction: column;
}

.face {
  width: 36px;
  height: 36px;
  border-radius: 36px;
}

.content {
  color: #333333;
  font-size: 14px;
  min-height: 20px;
  border-radius: 10px;
  padding: 0 15px;
  line-height: 1.4;
  word-break: break-all;
  word-wrap: break-word;
  position: relative;
  margin-top: 5px;
  box-shadow: 0 0 5px 5px rgba(0, 0, 0, 0.06);
  .quote-item {
    padding: 5px 10px 5px 0;
    border-radius: 10px;
    border: 1px solid #eeeeee;
    margin-bottom: 6px;
    cursor: pointer;
  }
}

.left {
  margin: 0 10px;
  .face {}
  .content {
    color: #333333;
    border: 1px solid #eeeeee;
    border-radius: 0 10px 10px 10px;
  }
}

.right {
  margin: 0 10px;
  flex-direction: row-reverse;
  .face {}
  .content {
    color: #41b584;
    background-color: #ecf8f3;
    border: 1px solid #41b584;
    border-radius: 10px 0 10px 10px;
  }
}

.quote-dialog-header {
  cursor: pointer;
  color: #333333;
  text-decoration: underline;
}

.quote-dialog-content-item {
  padding: 10px;
  border: 1px solid #eeeeee;
  border-radius: 10px;
  margin-bottom: 10px;
}

</style>
