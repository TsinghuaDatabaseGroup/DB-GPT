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
      <el-button icon="Promotion" type="success" :disabled="sendBtnDisabled" circle size="default" style="font-size: 22px;" @click="onSendClick"/>
    </div>
    <slot name="right">
      <div/>
    </slot>
  </div>
</template>

<script setup lang="ts" name="DiagnosisInputContainer">

import {ref} from "vue";

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

const onSendClick = () => {
  if (editData.value && editData.value.type === 'select') {
    userInput.value = selectValues.value.join(',')
  }
  emit('send-click', userInput.value)
  userInput.value = ''
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
