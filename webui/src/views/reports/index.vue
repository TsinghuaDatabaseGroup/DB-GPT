<template>
  <div class="rowSS" style="width: 100%; font-size: 1rem; line-height: 1.6!important;">
    <div class="columnSS" style=" width: 55%;">
      <div
          class="rowBC"
          style="margin: 20px 20px 0 ; border-radius: 80px!important; width: calc(100% - 40px)"
      >

        <div class="rowSC" style="margin-right: 10px">
          <span style="font-size: 14px; margin-right: 10px">{{ $t('modelTip') + ':' }}</span>
          <el-select v-model="model" style="width: 120px" placeholder="">
            <el-option
                v-for="item in modelList"
                :key="item"
                :label="item"
                :value="item"
            />
          </el-select>
        </div>

        <div class="rowSC" style="flex-shrink: 0">
          <span style="font-size: 14px; margin-right: 10px">{{ $t('playbackAnimationTip') + ':' }}</span>
          <el-switch
              v-model="skipTyped"
              active-color="#ff4949"
              inactive-color="#13ce66"
              active-text=""
              inactive-text=""
          />
        </div>

      </div>
      <div class="columnSS" style="height: calc(100vh - 100px); overflow-y: auto; margin: 10px 0; padding-left: 20px; width: 100%">
        <div
            v-for="(item, index) in historyMessages"
            :key="index"
            class="diagnose-item columnSS"
            style="background: RGBA(255, 255, 255, 1.00);"
        >
          <div class="rowBC w-full">
            <div class="rowSC w-full">
              <div v-for="(alert_item, alert_index) in item.alerts" :key="alert_index" class="rowSS" style="margin-right: 10px">
                <div :style="severityStyle[alert_item.alert_level]">
                  [{{ alert_item.alert_level }}{{ alert_item.alert_level !== 'INFO' ? '🔥' : '' }}]
                </div>
                <div style="color: #666666; margin-left: 5px">{{ alert_item.alert_name }}</div>
              </div>
              <div style="color: #999999; font-size: 12px; height: 12px; line-height: 12px; margin-top: 4px">{{ item.time }}</div>
            </div>
            <div class="rowSC">
              <el-button type="success" size="small" style="margin:0 10px" @click="onReviewClick(item)">{{ $t('playbackButton') }}<i
                  class="el-icon-video-camera-solid el-icon--right"
                  style="font-size: 16px"
              />
              </el-button>
              <el-button type="warning" size="small" @click="onReportClick(item, index)">{{ $t('reportButton') }}<i
                  class="el-icon-document-add el-icon--right"
                  style="font-size: 16px"
              /></el-button>
            </div>
          </div>
          <el-carousel
              v-if="openIndex === index && charts.length > 0"
              v-loading="openReportLoading"
              :interval="3000"
              arrow="always"
              direction="horizontal"
              height="260"
              style="background: RGBA(255, 255, 255, 1.00); padding: 10px; margin: 10px; border-radius: 8px; width: 100%"
              motion-blur
          >
            <el-carousel-item v-for="(chartItem, chartIndex) in charts" :key="chartIndex">
              <v-chart style="height: 240px; width: 100%;" :option="chartItem" autoresize/>
            </el-carousel-item>
          </el-carousel>
        </div>
      </div>
    </div>
    <div
        v-loading="openReportLoading"
        class="relative columnSS"
        style="overflow-y: scroll; height: 100vh; overflow-x: hidden; width: 45%; background: RGBA(255, 255, 255, 1.00);"
    >
      <div
          style="background-color: white; padding: 10px; margin: 10px; border-radius: 8px;"
          v-html="openReportContent"
      />
    </div>
    <el-drawer
        v-if="reviewDrawer"
        v-model="reviewDrawer"
        v-loading="reviewLoading"
        :title="$t('reviewDrawerTitle')"
        size="95vw"
        destroy-on-close
        direction="rtl"
    >
      <div class="relative columnSS" style="overflow: hidden; height: 100%">
        <el-steps :active="activeName" finish-status="success" simple style="width: 100%;">
          <el-step :title="$t('setpTitle1')" style="cursor: pointer" @click="onStepClick(0)"/>
          <el-step :title="$t('setpTitle2')" style="cursor: pointer" @click="onStepClick(1)"/>
          <el-step :title="$t('setpTitle3')" style="cursor: pointer" @click="onStepClick(2)"/>
        </el-steps>

        <transition name="fade">
          <div
              ref="setpScrollDiv"
              class="c-relative columnSS"
              style="height: calc(100% - 60px); overflow-y: auto; margin: 10px 0"
              @scroll="stepScrollEvent"
          >
            <div class="review-step">
              <div style="height: 40px; line-height: 40px; color: #333333; font-weight: bold; font-size: 18px">
                1.{{ $t('setpTip1') }}
              </div>
              <div class="rowSS c-align-items-center" style="height: calc(100% - 40px)">
                <report-one-chat
                    v-if="roleAssignerMessages.length > 0"
                    id="RoleAssigner"
                    key="RoleAssigner"
                    class="chat-container"
                    sender="RoleAssigner"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    :messages="roleAssignerMessages"
                    style="height: 100%; width: 30%;"
                    @playback-complete="onRoleAssignerPlaybackComplete('0')"
                />
                <div class="rowSS" style="width: 70%; height: 100%;">
                  <report-one-chat
                      v-if="cpuExpertMessages.length > 0"
                      id="CpuExpert"
                      key="CpuExpert"
                      sender="CpuExpert"
                      :type-speed="typeSpeed"
                      :skip-typed="skipTyped"
                      class="chat-container"
                      :messages="cpuExpertMessages"
                      style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                      @playback-complete="onPlaybackComplete(1)"
                  />
                  <report-one-chat
                      v-if="ioExpertMessages.length > 0"
                      id="IoExpert"
                      key="IoExpert"
                      sender="IoExpert"
                      :type-speed="typeSpeed"
                      :skip-typed="skipTyped"
                      class="chat-container"
                      :messages="ioExpertMessages"
                      style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                      @playback-complete="onPlaybackComplete(1)"
                  />
                  <report-one-chat
                      v-if="memoryExpertMessages.length > 0"
                      id="MemoryExpert"
                      key="MemoryExpert"
                      sender="MemoryExpert"
                      :type-speed="typeSpeed"
                      :skip-typed="skipTyped"
                      class="chat-container"
                      :messages="memoryExpertMessages"
                      style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                      @playback-complete="onPlaybackComplete(1)"
                  />
                  <report-one-chat
                      v-if="indexExpertMessages.length > 0"
                      id="IndexExpert"
                      key="IndexExpert"
                      sender="IndexExpert"
                      :type-speed="typeSpeed"
                      :skip-typed="skipTyped"
                      class="chat-container"
                      :messages="indexExpertMessages"
                      style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                      @playback-complete="onPlaybackComplete(1)"
                  />
                  <report-one-chat
                      v-if="configurationExpertMessages.length > 0"
                      id="ConfigurationExpert"
                      key="ConfigurationExpert"
                      sender="ConfigurationExpert"
                      :type-speed="typeSpeed"
                      :skip-typed="skipTyped"
                      class="chat-container"
                      :messages="configurationExpertMessages"
                      style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                      @playback-complete="onPlaybackComplete(1)"
                  />
                  <report-one-chat
                      v-if="queryExpertMessages.length > 0"
                      id="QueryExpert"
                      key="QueryExpert"
                      sender="QueryExpert"
                      :type-speed="typeSpeed"
                      :skip-typed="skipTyped"
                      class="chat-container"
                      :messages="queryExpertMessages"
                      style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                      @playback-complete="onPlaybackComplete(1)"
                  />
                  <report-one-chat
                      v-if="workloadExpertMessages.length > 0"
                      id="WorkloadExpert"
                      key="WorkloadExpert"
                      sender="WorkloadExpert"
                      :type-speed="typeSpeed"
                      :skip-typed="skipTyped"
                      class="chat-container"
                      :messages="workloadExpertMessages"
                      style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                      @playback-complete="onPlaybackComplete(1)"
                  />
                </div>
              </div>
            </div>

            <div class="review-step">
              <span style="height: 40px; line-height: 40px; color: #333333; font-weight: bold; margin: 10px 0; font-size: 18px">
                2.{{ $t('setpTip2') }}
              </span>
              <report-chat
                  v-if="brainstormingMessages.length > 0"
                  class="chat-container"
                  :type-speed="typeSpeed"
                  :skip-typed="skipTyped"
                  :messages="brainstormingMessages"
                  style="height: calc(100% - 40px); width: 100%; padding: 0"
                  @playback-complete="onBrainstormingPlaybackComplete()"
              />
            </div>

            <div class="review-step" style="margin-top: 30px">
              <span style="height: 40px; line-height: 40px; color: #333333; font-weight: bold; font-size: 18px">3.{{ $t('setpTip3') }}</span>
              <div style="width: 100%; padding: 10px; background-color: RGBA(242, 246, 255, 1); border-radius: 8px" v-html="reportContent"/>
            </div>
          </div>
        </transition>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>

import {alertHistories, alertHistoryDetail, diagnoseLlmModelList} from '@/api/report'
import ReportChat from '@/components/ReportChat.vue'
import ReportOneChat from '@/components/ReportOneChat.vue'
import {LineChart} from 'echarts/charts';
import {DataZoomComponent, LegendComponent, TitleComponent, TooltipComponent, GridComponent} from 'echarts/components';
import {use} from 'echarts/core';
import {CanvasRenderer} from 'echarts/renderers';
import hljs from 'highlight.js';
import "highlight.js/styles/gruvbox-dark.css";
import {Marked} from "marked";
import {markedHighlight} from "marked-highlight";
import {nextTick, onMounted, provide, reactive, ref, watch} from 'vue'
import VChart, {THEME_KEY} from 'vue-echarts';

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  GridComponent
]);

provide(THEME_KEY, 'light');

const marked = new Marked(
    markedHighlight({
      langPrefix: 'hljs language-',
      highlight(code, lang, info) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, {language}).value;
      }
    })
);

const timeRange = ref([]);
const openReport = ref('');
const openIndex = ref(-1);
const severityStyle = reactive({
  'CRIT': 'color: #F56C6C;',
  'WARN': 'color: #E6A23C;',
  'INFO': 'color: #909399;'
});
const expertCount = ref(0);
const roleAssignerMessages = ref([]);
const cpuExpertMessages = ref([]);
const ioExpertMessages = ref([]);
const memoryExpertMessages = ref([]);
const indexExpertMessages = ref([]);
const configurationExpertMessages = ref([]);
const queryExpertMessages = ref([]);
const workloadExpertMessages = ref([]);
const brainstormingMessages = ref([]);
const report = ref('');
const historyMessages = ref([]);
const reviewDrawer = ref(false);
const reviewItem = ref({});
const reviewLoading = ref(false);
const activeName = ref(0);
const skipTyped = ref(true);
const typeSpeed = ref(100);
const openReportLoading = ref(false);
const charts = ref([]);
const modelList = ref([]);
const model = ref('');
const setpScrollDiv = ref(null);
const lineChartOption = {
  title: {show: true},
  grid: {
    left: 80,
    top: 60,
    bottom: 40,
    right: 80
  },
  tooltip: {
    trigger: 'axis',
    textStyle: {
      align: 'left'
    },
    show: true,
    confine: true,
    axisPointer: {
      type: 'shadow'
    }
  },
  color: ['#1890FF', '#975FE4', '#FE2E2E', '#01DF01', '#3B94EF', '#1DED12'],
  xAxis: {
    splitArea: {
      show: true,
      interval: 0,
      areaStyle: {
        color: ['rgba(0, 0, 0, 0)']
      }
    },
    type: 'category',
    nameTextStyle: {
      color: '#666666'
    },
    axisLabel: {
      show: true,
      showMinLabel: true,
      fontSize: 10
    },
    axisLine: {
      show: true,
      lineStyle: {
        width: 0.5,
        color: '#999999',
        shadowColor: '#fff',
        shadowBlur: 10
      }
    },
    axisTick: {
      show: true,
      inside: true,
      length: 5,
      lineStyle: {
        width: 0.5,
        color: '#999999',
        shadowColor: '#fff',
        shadowBlur: 10
      }
    },
    data: []
  },
  yAxis: {
    type: 'value',
    offset: 0,
    nameTextStyle: {
      color: '#666666'
    },
    axisLabel: {
      show: true,
      showMinLabel: true,
      fontSize: 10
    },
    splitLine: {
      show: true,
      lineStyle: {
        color: '#e5e5e5',
        type: 'dotted'
      }
    },
    axisTick: {
      show: false
    }
  },
  series: [{
    name: '',
    data: [],
    type: 'line',
    smooth: true,
    showSymbol: false
  }]
}

watch(() => model, (val, oldVal) => {
  if (val) {
    console.log('model changed:', model)
    getAlertHistories()
  }
}, {deep: true})

const openReportContent = computed(() => {
  return marked.parse(openReport.value)
})

const reportContent = computed(() => {
  return marked.parse(report.value)
})

onMounted(getDiagnoseLlmModelList)

function getDiagnoseLlmModelList() {
  diagnoseLlmModelList().then(res => {
    modelList.value = res.data
    if (modelList.value.length > 0) {
      model.value = modelList.value[0]
    }
  }).finally(() => {
  })
}

function getAlertHistories() {
  historyMessages.value = []
  let reqData = {}
  if (timeRange.value && timeRange.value.length > 1) {
    reqData = {start: timeRange.value[0] / 1000, end: timeRange.value[1] / 1000}
  }
  reqData.model = model.value
  alertHistories(reqData.start || undefined, reqData.end || undefined, model.value).then(res => {
    console.log('getAlertHistories:', res)
    historyMessages.value = res.data
    onReportClick(historyMessages.value[0], 0)
  }).finally(() => {
  })
}

const timeRangeOnChange = () => {
  if (timeRange.value && timeRange.value.length > 1) {
    getAlertHistories()
  }
}

const onReviewClick = (item) => {
  reviewDrawer.value = true
  reviewItem.value = item
  reviewLoading.value = true
  getAlertHistoryDetail(item, () => {
    reviewLoading.value = false
  })
}

const onRoleAssignerPlaybackComplete = () => {
  expertCount.value = 0
  cpuExpertMessages.value = reviewItem.value.anomalyAnalysis?.CpuExpert?.messages || []
  ioExpertMessages.value = reviewItem.value.anomalyAnalysis?.IoExpert?.messages || []
  memoryExpertMessages.value = reviewItem.value.anomalyAnalysis?.MemoryExpert?.messages || []
  indexExpertMessages.value = reviewItem.value.anomalyAnalysis?.IndexExpert?.messages || []
  configurationExpertMessages.value = reviewItem.value.anomalyAnalysis?.ConfigurationExpert?.messages || []
  queryExpertMessages.value = reviewItem.value.anomalyAnalysis?.QueryExpert?.messages || []
  workloadExpertMessages.value = reviewItem.value.anomalyAnalysis?.WorkloadExpert?.messages || []

  expertCount.value += cpuExpertMessages.value.length > 0 ? 1 : 0
  expertCount.value += ioExpertMessages.value.length > 0 ? 1 : 0
  expertCount.value += memoryExpertMessages.value.length > 0 ? 1 : 0
  expertCount.value += indexExpertMessages.value.length > 0 ? 1 : 0
  expertCount.value += configurationExpertMessages.value.length > 0 ? 1 : 0
  expertCount.value += queryExpertMessages.value.length > 0 ? 1 : 0
  expertCount.value += workloadExpertMessages.value.length > 0 ? 1 : 0


}

function onPlaybackComplete(value) {
  expertCount.value -= value
  if (expertCount.value <= 0) {
    brainstormingMessages.value = reviewItem.value.brainstorming?.messages || []
    onStepClick(1)
  }
}

function onBrainstormingPlaybackComplete() {
  onStepClick(2)
  report.value = reviewItem.value.report || ''
}

function getAlertHistoryDetail(item, callback) {
  roleAssignerMessages.value = []
  cpuExpertMessages.value = []
  ioExpertMessages.value = []
  memoryExpertMessages.value = []
  indexExpertMessages.value = []
  configurationExpertMessages.value = []
  queryExpertMessages.value = []
  workloadExpertMessages.value = []
  brainstormingMessages.value.values = []
  alertHistoryDetail(item.file_name, model.value).then(res => {
    reviewItem.value = res.data
    roleAssignerMessages.value = reviewItem.value.anomalyAnalysis.RoleAssigner.messages || []
    if (callback) {
      callback()
    }
  }).finally(() => {
    reviewLoading.value = false
  })
}

function onReportClick(item, index) {
  openReportLoading.value = true
  openIndex.value = index
  charts.value = []
  getAlertHistoryDetail(item, () => {
    openReportLoading.value = false
    openReport.value = reviewItem.value.report || ''
    const topMetrics = reviewItem.value.topMetrics
    topMetrics.forEach(item => {
      const option = JSON.parse(JSON.stringify(lineChartOption))
      option.series[0].data = item.values
      option.title.text = item.title
      option.color = option.color[Math.floor(Math.random() * option.color.length)]
      charts.value.push(option)
    })
    console.log('=======>', charts.value)
  })
}

function onStepClick(index) {
  activeName.value = index
  const calcHeight = setpScrollDiv.value.getBoundingClientRect().height
  scrollToTopWithAnimation(calcHeight * index)
}

const scrollToTopWithAnimation = (scrollTop) => {
  nextTick(() => {
    setTimeout(() => {
      if (setpScrollDiv.value) {
        setpScrollDiv.value.scrollTo({top: scrollTop, behavior: 'smooth'});
      }
    }, 0);
  })
}

const stepScrollEvent = () => {
  if (setpScrollDiv.value) {
    const calcHeight = setpScrollDiv.value.getBoundingClientRect().height;
    activeName.value = Number.parseInt(setpScrollDiv.value.scrollTop / calcHeight + 0.5);
  }
}

</script>
<style>

.hljs {
  word-break: break-all;
  white-space: pre-wrap;
  padding: 10px;
  border-radius: 4px;
}

.severity {
  width: 16px;
  height: 16px;
  border-radius: 16px;
  margin-right: 6px
}

h1, h2, h3, h4, h5, h6 {
  color: #333;
  font-weight: bold;
}

.el-input__inner {
  border-radius: 20px;
}

.el-input--suffix .el-input__inner {
  padding-right: 10px;
}

.el-drawer__header {
  margin-bottom: 10px !important;
  border: none;
}

.el-drawer {
  border-bottom-left-radius: 12px;
  border-top-left-radius: 12px;
  padding: 0 20px;
  /*background-color: RGBA(247, 250, 255, 1);*/
}

table {
  max-width: 100%;
  background-color: transparent;
  border-collapse: collapse;
  width: 100%;
}

table th,
table td {
  padding: 8px;
  line-height: 1.5;
  text-align: left;
  vertical-align: top;
  border: 1px solid #e1e1e1;
}

table th {
  font-weight: bold;
}

table caption + thead tr:first-child th,
table caption + thead tr:first-child td,
table colgroup + thead tr:first-child th,
table colgroup + thead tr:first-child td,
table thead:first-child tr:first-child th,
table thead:first-child tr:first-child td {
  border: 1px solid #e1e1e1;
  background-color: #f5f5f5;
}

.el-carousel__button {
  background-color: #999999 !important;
}

.el-carousel__container {
  height: 260px !important;
}

</style>

<style lang="scss" scoped>

.chat-container {
  overflow-y: scroll;
  background: RGBA(242, 246, 255, 1.00);
  border-radius: 12px;
  flex-shrink: 0
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.review-step {
  width: 100%;
  height: calc(100vh - 120px);
  flex-shrink: 0;
}

.container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.diagnose-item {
  flex-shrink: 1;
  padding: 10px 20px;
  margin-bottom: 10px;
  border-bottom-left-radius: 10px;
  border-top-left-radius: 10px;
  transition: height 3s ease-in-out;
  width: 100%;

  .title {
    color: #333333;
    font-size: 16px;
  }
}

.breathing-box {
  box-shadow: 0 0 5px 5px RGBA(103, 194, 58, 0.5);
  animation: breathing 1.8s infinite alternate;
}

@keyframes breathing {
  0% {
    box-shadow: 0 5px 5px RGBA(103, 194, 58, 0.2);
  }
  100% {
    box-shadow: 0 0 5px 5px RGBA(103, 194, 58, 0.5);
  }
}
</style>
