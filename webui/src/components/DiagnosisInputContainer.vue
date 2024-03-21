<template>
  <div className="diagnose-bottom-input-container">
    <slot name="left">
      <div/>
    </slot>
    <div className="diagnose-input-container">
      <template v-if="editData && editData.type === 'select'">
        <el-select
            v-model="selectValues"
            size="default"
            placeholder="Please select"
            multiple
            style="width: calc(100% - 40px); font-size: 14px;">
          <el-option
              v-for="selectItem in editData?.selectList"
              :key="selectItem"
              :label="selectItem"
              :value="selectItem"
          />
        </el-select>
      </template>
      <template v-else>
        <el-input
            v-model="userInput"
            :disabled=inputDisabled
            :placeholder="placeholder"
            clearable
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            size="default"
            style="width: calc(100% - 40px); font-size: 14px"
        />
      </template>
      <el-button icon="Promotion" type="success" :disabled="sendBtnDisabled || inputDisabled" circle size="default" style="font-size: 22px; margin-left: 10px"
                 @click="onSendClick"/>

      <el-tooltip
          class="box-item"
          effect="dark"
          content="Continue Diagnosis"
          placement="top-start"
      >
        <el-button style="margin-left: 10px;" :disabled="inputDisabled" circle size="default"  @click="onContinueClick">
          <svg t="1710861862028" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5408" width="32" height="32"><path d="M512 85.333333c235.264 0 426.666667 191.402667 426.666667 426.666667s-191.402667 426.666667-426.666667 426.666667S85.333333 747.264 85.333333 512 276.736 85.333333 512 85.333333z m0-85.333333C229.248 0 0 229.248 0 512s229.248 512 512 512 512-229.248 512-512S794.752 0 512 0z m42.666667 512l-256 170.624V341.376L554.666667 512z m0-170.624v341.248L810.666667 512l-256-170.624z" p-id="5409" fill="#4e8e2f"></path></svg>
        </el-button>
      </el-tooltip>

    </div>
    <slot name="right">
      <div/>
    </slot>
  </div>
</template>

<script setup lang="ts" name="DiagnosisInputContainer">

import {ref, warn} from "vue";

const props = defineProps({
  placeholder: {
    require: true,
    default: '请输入你的需求',
    type: String
  },
  editData: {
    require: false,
    default: null,
    type: Object
  },
  inputDisabled: {
    require: false,
    default: false,
    type: Boolean
  }
})

const selectValues = ref([])

const emit = defineEmits(['send-click'])

const userInput: Ref<string> = ref('')

const sendBtnDisabled = computed(() => userInput.value === '' && selectValues.value.length === 0)

watch (() => props.editData, (newVal) => {
  if (newVal && newVal.type !== 'select') {
    userInput.value = props.editData?.data || ''
  }
}, {immediate: true, deep: true})

const onSendClick = () => {
  if (props.editData && props.editData.type === 'select') {
    userInput.value = JSON.stringify(selectValues.value)
    selectValues.value = []
  }
  emit('send-click', userInput.value)
  userInput.value = ''
}

const onContinueClick = () => {
  emit('send-click', 'continue')
}

</script>

<style>
.diagnose-input-container .el-input__wrapper {
  border: None !important;
  box-shadow: None !important;
}
.diagnose-input-container .el-select__wrapper {
  padding: 8px 16px!important;
}
</style>

<style lang="scss" scoped>
.diagnose-bottom-input-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.diagnose-input-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  flex-shrink: 1;
  border-radius: 15px;
  background: white;
  overflow: hidden;
  padding: 10px;
  border: 1px solid rgba(0, 0, 0, 0.12);
}

</style>
