<template>
  <div class="c-flex-row" style="width: 100%; font-size: 1rem; line-height: 1.6!important; height: 1000px">
    <div class="c-flex-column" style=" width: 55%;">
      <div
        class="c-flex-row c-align-items-center c-justify-content-between c-shaow-card"
        style="padding: 10px 20px; border-radius: 80px!important;"
      >
        <el-form
          ref="form"
          :inline="true"
          label-position="left"
        >
          <el-form-item :label="$t('modelTip') + ':'" style="margin-bottom: 0">
            <el-select v-model="model" placeholder="" @change="getAlertHistories">
              <el-option
                v-for="item in modelList"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

        </el-form>

        <div class="c-flex-row c-align-items-center" style="flex-shrink: 0">
          <el-switch
            v-model="skipTyped"
            style="display: block"
            active-color="#ff4949"
            inactive-color="#13ce66"
            active-text=""
            :inactive-text="$t('playbackAnimationTip')"
          />
          <div class="c-flex-row" style="margin-left: 20px" @click="onEnClick">
            <img src="@/assets/ch_to_en.png" style="width: 30px; height: 30px;">
          </div>
        </div>

      </div>
      <div class="c-flex c-flex-column" style="height: calc(100vh - 100px); overflow-y: auto; margin: 10px 0; padding: 0 10px">
        <div
          v-for="(item, index) in historyMessages"
          :key="index"
          class="diagnose-item c-flex-column"
          style="background: RGBA(255, 255, 255, 1.00);"
        >
          <div class="c-flex-row c-align-items-center c-justify-content-between">
            <div class="c-flex-row c-align-items-center c-justify-content-left">
              <div v-for="(alert_item, alert_index) in item.alerts" :key="alert_index" class="c-flex-row c-justify-content-left" style="margin-right: 10px">
                <div :style="severityStyle[alert_item.alert_level]">
                  [{{ alert_item.alert_level }}{{ alert_item.alert_level !== 'INFO' ? '🔥' : '' }}]
                </div>
                <div style="color: #666666; margin-left: 5px">{{ alert_item.alert_name }}</div>
              </div>
              <div style="color: #999999; font-size: 12px; height: 12px; line-height: 12px; margin-top: 4px">{{ item.report_generate_time }}</div>
            </div>
            <div class="c-flex-row c-align-items-center">
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
<!--          <el-collapse-transition>-->
<!--            <el-carousel-->
<!--              v-if="openIndex === index && charts.length > 0"-->
<!--              :interval="3000"-->
<!--              arrow="always"-->
<!--              height="260"-->
<!--              style="background: RGBA(255, 255, 255, 1.00); padding: 10px; margin: 10px; border-radius: 8px;"-->
<!--            >-->
<!--              <el-carousel-item v-for="(chartItem, chartIndex) in charts" :key="chartIndex">-->
<!--                <lineChart-->
<!--                  style="height: 200px; width: calc(100% - 40px);"-->
<!--                  :chart-option="chartItem"-->
<!--                />-->
<!--              </el-carousel-item>-->
<!--            </el-carousel>-->
<!--          </el-collapse-transition>-->
        </div>
      </div>
    </div>
    <div
      class="c-relative c-flex-column"
      style="overflow-y: scroll; height: 100vh; overflow-x: hidden; width: 45%; background: RGBA(255, 255, 255, 1.00);"
    >
      <div
        style="background-color: white; padding: 0 10px; margin: 0 10px; border-radius: 8px;"
        v-html="openReport"
      />
    </div>
    <el-drawer
      v-if="reviewDrawer"
      v-loading="reviewLoading"
      :title="$t('reviewDrawerTitle')"
      :visible.sync="reviewDrawer"
      size="95vw"
      destroy-on-close
      direction="rtl"
    >
      <div class="c-relative c-flex-column" style="overflow: hidden; height: 100%">
        <el-steps :active="activeName" finish-status="success" simple style="width: 100%;">
          <el-step :title="$t('setpTitle1')" style="cursor: pointer" @click.n.native="onStepClick(0)" />
          <el-step :title="$t('setpTitle2')" style="cursor: pointer" @click.n.native="onStepClick(1)" />
          <el-step :title="$t('setpTitle3')" style="cursor: pointer" @click.n.native="onStepClick(2)" />
        </el-steps>

        <transition name="fade">
          <div
            ref="setpScrollDiv"
            class="c-relative c-flex-column"
            style="height: calc(199 - 60px); overflow-y: auto; margin: 10px 0"
            @scroll="stepScrollEvent"
          >
            <div class="review-step">
              <div style="height: 40px; line-height: 40px; color: #333333; font-weight: bold; font-size: 18px">
                1.{{ $t('setpTip1') }}
              </div>
              <div class="c-flex-row c-align-items-center" style="height: calc(100% - 40px)">
                <OneChat
                  v-if="roleAssignerMessages.length > 0"
                  id="RoleAssigner"
                  key="RoleAssigner"
                  class="chat-container"
                  sender="RoleAssigner"
                  :type-speed="typeSpeed"
                  :skip-typed="skipTyped"
                  :messages="roleAssignerMessages"
                  style="height: 100%; width: 30%;"
                  @playbackComplete="onRoleAssignerPlaybackComplete('0')"
                />
                <div class="c-flex-row" style="width: 70%; height: 100%;">
                  <OneChat
                    v-if="cpuExpertMessages.length > 0"
                    id="CpuExpert"
                    key="CpuExpert"
                    sender="CpuExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="cpuExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                    @playbackComplete="onPlaybackComplete(1)"
                  />
                  <OneChat
                    v-if="ioExpertMessages.length > 0"
                    id="IoExpert"
                    key="IoExpert"
                    sender="IoExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="ioExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                    @playbackComplete="onPlaybackComplete(1)"
                  />
                  <OneChat
                    v-if="memoryExpertMessages.length > 0"
                    id="MemoryExpert"
                    key="MemoryExpert"
                    sender="MemoryExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="memoryExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                    @playbackComplete="onPlaybackComplete(1)"
                  />
                  <OneChat
                    v-if="indexExpertMessages.length > 0"
                    id="IndexExpert"
                    key="IndexExpert"
                    sender="IndexExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="indexExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                    @playbackComplete="onPlaybackComplete(1)"
                  />
                  <OneChat
                    v-if="configurationExpertMessages.length > 0"
                    id="ConfigurationExpert"
                    key="ConfigurationExpert"
                    sender="ConfigurationExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="configurationExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                    @playbackComplete="onPlaybackComplete(1)"
                  />
                  <OneChat
                    v-if="queryExpertMessages.length > 0"
                    id="QueryExpert"
                    key="QueryExpert"
                    sender="QueryExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="queryExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                    @playbackComplete="onPlaybackComplete(1)"
                  />
                  <OneChat
                    v-if="workloadExpertMessages.length > 0"
                    id="WorkloadExpert"
                    key="WorkloadExpert"
                    sender="WorkloadExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="workloadExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                    @playbackComplete="onPlaybackComplete(1)"
                  />
                </div>
              </div>
            </div>

            <div class="review-step">
              <span style="height: 40px; line-height: 40px; color: #333333; font-weight: bold; margin: 10px 0; font-size: 18px">
                2.{{ $t('setpTip2') }}
              </span>
              <Chat
                v-if="brainstormingMessages.length > 0"
                class="chat-container"
                :type-speed="typeSpeed"
                :skip-typed="skipTyped"
                :messages="brainstormingMessages"
                style="height: calc(100% - 40px); width: 100%; padding: 0"
                @playbackComplete="onBrainstormingPlaybackComplete()"
              />
            </div>

            <div class="review-step">
              <span style="height: 40px; line-height: 40px; color: #333333; font-weight: bold; font-size: 18px">3.{{ $t('setpTip3') }}</span>
              <div style="width: 100%; padding: 10px; background-color: RGBA(242, 246, 255, 1); border-radius: 8px" v-html="report" />
            </div>
          </div>
        </transition>
      </div>
    </el-drawer>
  </div>
</template>

<script>

import Vue from 'vue'
import Chat from '@/components/Chat'
import OneChat from '@/components/OneChat'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
// import lineChart from '@/components/echarts/vue-chart'
// import { lineChartOption } from '@/utils/echart-ori-options'
import { Streamlit } from "streamlit-component-lib";

export default {
  filters: {},
  props: ["args"],
  components: { OneChat, Chat },
  data() {
    return {
      timeRange: [],
      messages: [],
      openReport: '',
      openIndex: -1,
      severityStyle: {
        'CRIT': 'color: #F56C6C;',
        'WARN': 'color: #E6A23C;',
        'INFO': 'color: #909399;'
      },
      md: undefined,
      expertCount: 0,
      roleAssignerMessages: [],
      cpuExpertMessages: [],
      ioExpertMessages: [],
      memoryExpertMessages: [],
      indexExpertMessages: [],
      configurationExpertMessages: [],
      queryExpertMessages: [],
      workloadExpertMessages: [],
      brainstormingMessages: [],
      tableMessages: [],
      report: '',
      introMessage: [],
      historyMessages: [],
      historyLoading: false,
      reviewDrawer: false,
      reviewItem: {},
      reviewLoading: false,
      activeName: 0,
      analyseAt: undefined,
      skipTyped: true,
      typeSpeed: 100,
      charts: [],
      modelList: [],
      model: ''
    }
  },
  computed: {},
  watch: {
    args: {
      handler: function(val, oldVal) {
        console.log('args changed from:', oldVal)
        console.log('args changed to:', val)
        if (val) {
          this.$nextTick(() => {
            this.modelList = val.modelList || []
            this.model = val.currentModel || this.modelList[0]
            this.historyMessages = val.diagnoseHistories || []
            if (this.historyMessages.length > 0) {
              this.onReportClick(this.historyMessages[0], 0)
            }
          })
        }
      },
      deep: true,
      immediate: true
    }
  },
  mounted() {
    this.md = new MarkdownIt()
        .set({ html: true, breaks: true, typographer: true, linkify: true })
        .set({
          highlight: function(code) {
            return '<pre class="hljs"><code>' +
                hljs.highlight(code, { language: 'python', ignoreIllegals: true }).value +
                '</code></pre>'
          }
        })
  },
  methods: {
    onEnClick() {
      this.$i18n.locale = this.$i18n.locale === 'en' ? 'zh' : 'en'
      localStorage.setItem('LanguageSwitching', this.$i18n.locale)
    },
    getAlertHistories() {
      const data = {model: this.model}
      Streamlit.setComponentValue(data)
    },
    onReviewClick(item) {
      this.reviewLoading = true
      this.activeName = 0
      this.reviewDrawer = true
      this.getAlertHistoryDetail(item)
    },
    onRoleAssignerPlaybackComplete() {
      this.expertCount = 0
      this.cpuExpertMessages = this.reviewItem.anomalyAnalysis?.CpuExpert?.messages || []
      this.ioExpertMessages = this.reviewItem.anomalyAnalysis?.IoExpert?.messages || []
      this.memoryExpertMessages = this.reviewItem.anomalyAnalysis?.MemoryExpert?.messages || []
      this.indexExpertMessages = this.reviewItem.anomalyAnalysis?.IndexExpert?.messages || []
      this.configurationExpertMessages = this.reviewItem.anomalyAnalysis?.ConfigurationExpert?.messages || []
      this.queryExpertMessages = this.reviewItem.anomalyAnalysis?.QueryExpert?.messages || []
      this.workloadExpertMessages = this.reviewItem.anomalyAnalysis?.WorkloadExpert?.messages || []

      this.expertCount += this.cpuExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.ioExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.memoryExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.indexExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.configurationExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.queryExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.workloadExpertMessages.length > 0 ? 1 : 0
    },
    onPlaybackComplete(value) {
      this.expertCount -= value
      if (this.expertCount <= 0) {
        this.brainstormingMessages = this.reviewItem.brainstorming?.messages || []
        this.onStepClick(1)
      }
    },
    onBrainstormingPlaybackComplete() {
      this.onStepClick(2)
      this.report = this.md.render(this.reviewItem.report || '')
    },
    getAlertHistoryDetail(item) {
      this.roleAssignerMessages = []
      this.cpuExpertMessages = []
      this.ioExpertMessages = []
      this.memoryExpertMessages = []
      this.indexExpertMessages = []
      this.configurationExpertMessages = []
      this.queryExpertMessages = []
      this.workloadExpertMessages = []
      this.brainstormingMessages = []
      this.reviewItem = item
      console.log(this.reviewItem)
      this.roleAssignerMessages = this.reviewItem.anomalyAnalysis.RoleAssigner.messages || []
      this.reviewLoading = false
    },
    onReportClick(item, index) {
      this.openIndex = index
      this.charts = []
      this.getAlertHistoryDetail(item)
      this.openReport = this.md.render(this.reviewItem.report || '')
      // const topMetrics = this.reviewItem.topMetrics || []
      // topMetrics.forEach(item => {
      //   const option = JSON.parse(JSON.stringify(lineChartOption))
      //   option.series[0].data = item.values
      //   option.title.text = item.title
      //   option.color = option.color[Math.floor(Math.random() * option.color.length)]
      //   this.charts.push(option)
      // })
    },
    onStepClick(activeName) {
      this.activeName = activeName
      const calcHeight = this.$refs.setpScrollDiv.getBoundingClientRect().height
      this.scrollToTopWithAnimation(calcHeight * this.activeName)
    },
    scrollToTopWithAnimation(scrollTop) {
      Vue.nextTick(() => {
        setTimeout(() => {
          if (this.$refs['setpScrollDiv']) {
            this.$refs.setpScrollDiv.scrollTo({ top: scrollTop, behavior: 'smooth' })
          }
        }, 0)
      })
    },
    stepScrollEvent() {
      if (this.$refs['setpScrollDiv']) {
        const calcHeight = this.$refs.setpScrollDiv.getBoundingClientRect().height
        this.activeName = parseInt(this.$refs.setpScrollDiv.scrollTop / calcHeight + 0.5)
      }
    }
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
  height: 260px!important;
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
  flex-shrink: 0;
  padding: 10px 0;
  margin-bottom: 10px;
  border-bottom-left-radius: 10px;
  border-top-left-radius: 10px;
  transition: height 3s ease-in-out;
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
