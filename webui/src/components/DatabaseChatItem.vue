<template>
  <div class="chat-item-container">
    <div :class="'rowSC ' + roleClass">
      <img v-if="isUser" src="@/assets/chat-user.png" class="face"/>
      <img v-else src="@/assets/chat-robot.png" class="face" />
    </div>
    <div :class="'rowSC ' + roleClass">
      <div class="columnSS content">
        <template v-if="isUser">
          <div v-html="htmlContent" />
        </template>
        <template v-else>
          <div style="min-width: 30vw; padding-bottom: 10px">
            <div>
              <el-divider content-position="left">
                <div class="rowSC">
                  <el-icon size="18" style="margin-right: 5px"  :color="currentStep > 0 ? 'var(--el-color-success)': ''" ><Printer /></el-icon>
                  {{currentStep === 0 ? '语句生成中' : '生成语句成功'}}
                  <el-icon v-if="currentStep < 1 && message.loading" class="is-loading" size="20" color="#333333" style="margin-left: 5px;">
                    <Loading />
                  </el-icon>
                </div>
              </el-divider>
              <span style="line-height: 20px; color: #333333">{{ message.query }}</span>
            </div>
            <div v-if="currentStep >= 1">
              <el-divider content-position="left">
                <div class="rowSC">
                  <el-icon size="18" style="margin-right: 5px" :color="currentStep > 1 ? 'var(--el-color-success)': ''" ><Coin /></el-icon>
                  {{currentStep === 1 ? '数据查询中' : '数据获取成功'}}
                  <el-icon v-if="currentStep < 2 && message.loading" class="is-loading" size="20" color="#333333" style="margin-left: 5px;">
                    <Loading />
                  </el-icon>
                </div>
              </el-divider>
              <el-table v-if="queryResultData.length > 0" :data="queryResultData" style="width: 100%" height="200" border>
                <el-table-column
                    v-for="(item, index) in columnNames"
                    :key="index"
                    :prop="item"
                    :label="item"/>
              </el-table>
            </div>
            <div v-if="currentStep >= 2">
              <el-divider content-position="left">
                <div class="rowSC">
                  <el-icon size="18" style="margin-right: 5px" :color="currentStep > 2 ? 'var(--el-color-success)': ''" ><Histogram /></el-icon>
                  {{currentStep ===2 ? '对数据进行可视化' : '执行可视化成功'}}
                  <el-icon v-if="currentStep < 3 && message.loading" class="is-loading" size="20" color="#333333" style="margin-left: 5px;">
                    <Loading />
                  </el-icon>
                </div>
              </el-divider>
              <template v-if="Object.keys(message.queryChatOption).length > 0">
                <span style="line-height: 20px; color: #333333; margin-bottom: 10px">{{ message.queryChatOption.reason }}</span>
                <DatabaseChart style="width: 100%; height: 200px" :type="chartType" :xdata="xAxisData" :ydata="yAxisData" />
              </template>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 获取store和router
import DatabaseChart from "@/components/DatabaseChart.vue";
import marked from '@/utils/markdownConfig.js'

const props = defineProps({
  message: {required:true, type: Object, default: null },
  isLast: {required:true, type: Boolean, default: false }
})

const isUser = computed(() => props.message.role === 'user')

const roleClass = computed(() => props.message.role === 'user' ? 'right' : 'left')

const currentStep = computed(() => {

  if (!props.message.query) {
    return 0;
  }

  const hasQueryResult = Object.keys(props.message.queryResult).length > 0;
  const hasChatOptions = Object.keys(props.message.queryChatOption).length > 0;

  if (!hasQueryResult && !hasChatOptions) {
    return 1;
  }

  if (hasQueryResult && !hasChatOptions) {
    return 2;
  }

  if (hasQueryResult && hasChatOptions) {
    return 3;
  }

  return 4;
});

const htmlContent = computed(() => {
  return marked.parse(props.message.content)
})

const columnNames = computed(() => {
  if (!props.message.queryResult) {
    return []
  }
  return props.message.queryResult.column_names || []
})

const resultData = computed(() => {
  if (!props.message.queryResult) {
    return []
  }
  return props.message.queryResult.data || []
})

const queryResultData = computed(() => {
  const result =  resultData.value.map(item => {
    const obj = {}
    columnNames.value.forEach((key, index) => {
      obj[key] = item[index]
    })
    return obj
  })
  return result
})

const chartType = computed(() => {
  if (Object.keys(props.message.queryChatOption).length === 0) {
    return ""
  }
  const method = props.message.queryChatOption.method;
  switch (method) {
    case '折线图':
      return 'line'
    case '柱状图':
      return 'bar'
    case '饼状图':
      return 'pie'
    case '散点图':
      return 'scatter'
    default:
      return ''
  }
})

const xAxisData = computed(() => {
  if (!props.message.queryChatOption || Object.keys(props.message.queryChatOption).length === 0 || Object.keys(props.message.queryChatOption.design).length === 0) {
    return []
  }
  if (chartType.value !== 'pie') {
    const xAxisField = props.message.queryChatOption.design.xAxis;
    return resultData.value.map(item => item[columnNames.value.indexOf(xAxisField)]);
  }else {
    const xAxisField = props.message.queryChatOption.design.pie_name;
    return resultData.value.map(item => item[columnNames.value.indexOf(xAxisField)]);
  }
});

const yAxisData = computed(() => {
  if (!props.message.queryChatOption || Object.keys(props.message.queryChatOption).length === 0 || Object.keys(props.message.queryChatOption.design).length === 0) {
    return []
  }
  if (chartType.value !== 'pie') {
    const yAxisField = props.message.queryChatOption.design.yAxis;
    return resultData.value.map(item => item[columnNames.value.indexOf(yAxisField)]);
  }else {
    const yAxisField = props.message.queryChatOption.design.value;
    return resultData.value.map(item => item[columnNames.value.indexOf(yAxisField)]);
  }

});


</script>

<style>
.hljs {
  border-radius: 8px!important;
  padding: 10px!important;
}
.quote-dialog .el-dialog__body {
  padding: 10px 20px;
}
.el-divider__text {
  background-color: RGBA(251, 251, 252, 1.00);
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
