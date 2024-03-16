<template>
  <div class="bottom-input-container">
    <slot name="left">
      <div />
    </slot>
    <div class="input-container">
      <el-input
          v-model="userInput"
          :disabled=inputDisabled
          :placeholder="placeholder"
          clearable
          size="default"
          style="width: calc(100% - 40px);"
      />
      <el-button icon="Promotion" type="success" :disabled="sendBtnDisabled" circle size="default" style="font-size: 22px;" @click="onSendClick" />
    </div>
    <slot name="right">
      <div />
    </slot>
  </div>
</template>

<script setup lang="ts" name="BottomInputContainer">

import {ref} from "vue";

const props = defineProps({
  placeholder: {
    require: true,
    default: '请输入你的需求',
    type: String
  },
  inputDisabled: {
    require: false,
    default: false,
    type: Boolean
  }
})

const emit = defineEmits(['send-click'])

const userInput: Ref<string> = ref('')

const sendBtnDisabled = computed(() => userInput.value === '')

const onSendClick = () => {
  emit('send-click', userInput.value)
  userInput.value = ''
}

</script>

<style>
.input-container .el-input__wrapper {
  border: None !important;
  box-shadow: None !important;
}
</style>

<style lang="scss" scoped>
.bottom-input-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.input-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  width: 100%;
  flex-shrink: 1;
  border-radius: 15px;
  background: white;
  overflow: hidden;
  padding: 10px;
  border: 1px solid rgba(0, 0, 0, 0.12);
}

</style>
