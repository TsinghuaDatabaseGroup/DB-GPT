<template>
  <div class="c-flex-column" style=" width: 100%;">

    <div
      class="c-flex-row c-align-items-center c-justify-content-between c-shaow-card"
      style="padding: 10px 20px; margin: 0 20px; border-radius: 80px!important;"
    >
      <el-form
        ref="form"
        :inline="true"
        label-position="left"
      >
        <el-form-item :label="$t('queryTimeTip') + ':'" style="margin-bottom: 0">
          <el-date-picker
            v-model="timeRange"
            type="datetimerange"
            range-separator="-"
            format="yyyy-MM-dd HH:mm:ss"
            value-format="timestamp"
            :start-placeholder="$t('timeStartTip')"
            :end-placeholder="$t('timeEndTip')"
            :clearable="false"
            @change="timeRangeOnChange"
          />
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

        <div class="c-flex-row c-align-items-center" style="margin-left: 20px">
          <span :style="skipTyped ? 'color: #999999' : 'color: #000000'">{{ $t('animationSpeedTip') }}</span>
          <el-slider v-model="typeSpeed" :disabled="skipTyped" style="width: 200px; margin-left: 20px" />
        </div>

      </div>

    </div>

    <div class="c-flex c-flex-column" style="height: calc(100vh - 120px); overflow-y: auto; margin: 10px 0; padding: 0 20px">
      <div v-for="(item, index) in historyMessages" :key="index" class="diagnose-item c-flex-row c-align-items-center c-justify-content-between">
        <div class="c-flex-row c-align-items-center">
          <div class="title" style="margin-right: 20px">{{ item.title }}</div>
        </div>
        <div class="c-flex-row c-align-items-center">

          <div v-for="(alert_item, alert_index) in item.alerts" :key="alert_index" class="c-flex-row">
            <div class="severity" :style="severityStyle[alert_item.alert_level]" />
            <div style="color: #666666">{{ alert_item.alert_name }}</div>
          </div>

        </div>
        <div class="c-flex-row c-align-items-center">
          <el-button type="success" size="small" style="margin:0 10px" @click="onReviewClick(item)">{{ $t('playbackButton') }}<i
            class="el-icon-video-camera-solid el-icon--right"
            style="font-size: 16px"
          /></el-button>
          <el-button type="warning" size="small" @click="onReportClick(item)">{{ $t('reportButton') }}<i
            class="el-icon-document-add el-icon--right"
            style="font-size: 16px"
          /></el-button>
        </div>
      </div>
    </div>

    <el-drawer
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
                    v-if="networkExpertMessages.length > 0"
                    id="NetworkExpert"
                    key="NetworkExpert"
                    sender="NetworkExpert"
                    :type-speed="typeSpeed"
                    :skip-typed="skipTyped"
                    class="chat-container"
                    :messages="networkExpertMessages"
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
              <div style="width: 100%; padding: 10px; background-color: RGBA(242, 246, 255, 1); border-radius: 8px" v-html="md.render(report)" />
            </div>
          </div>
        </transition>
      </div>
    </el-drawer>

    <el-drawer
      :title="$t('reportDrawerTitle')"
      :visible.sync="reportDrawer"
      size="95vw"
      destroy-on-close
      direction="rtl"
    >
      <div class="c-relative c-flex-column" style="overflow-y: scroll; height: calc(100% - 40px); overflow-x: hidden">
        <div
          style="height: 100%; width: 100%; padding: 20px; background-color: RGBA(242, 246, 255, 1); border-radius: 8px;"
          v-html="md.render(report)"
        />
      </div>
    </el-drawer>

  </div>
</template>

<script>

import { alertHistories, alertHistoryDetail } from '@/api/api'
import Vue from 'vue'
import Chat from '@/components/Chat'
import OneChat from '@/components/OneChat'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

export default {
  filters: {},
  components: { OneChat, Chat },
  data() {
    return {
      timeRange: [],
      messages: [],
      severityStyle: {
        'CRIT': 'background-color: #F56C6C;',
        'WARN': 'background-color: #E6A23C;',
        'INFO': 'background-color: #909399;'
      },
      md: new MarkdownIt()
        .set({ html: true, breaks: true, typographer: true, linkify: true })
        .set({ highlight: function(code) {
          return '<pre class="hljs"><code>' +
              hljs.highlight(code, { language: 'python', ignoreIllegals: true }).value +
              '</code></pre>'
        } }),
      expertCount: 0,
      roleAssignerMessages: [],
      cpuExpertMessages: [],
      ioExpertMessages: [],
      memoryExpertMessages: [],
      networkExpertMessages: [],
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
      reportDrawer: false,
      skipTyped: true,
      typeSpeed: 100
    }
  },
  watch: {},
  mounted() {
    this.getAlertHistories()
  },
  methods: {
    customHighlight(code, lang) {
      const highlightedCode = hljs.highlight(lang, code).value
      return `<pre class="hljs"><code>${highlightedCode}</code></pre>`
    },
    getAlertHistories() {
      this.historyMessages = []
      alertHistories().then(res => {
        this.historyMessages = res.data
      }).finally(() => {
      })
    },
    timeRangeOnChange() {
      if (this.timeRange && this.timeRange.length > 1) {
        this.reloadRequest()
      }
    },
    onReviewClick(item) {
      this.reviewLoading = true
      this.activeName = 0
      this.reviewDrawer = true
      this.getAlertHistoryDetail(item)
    },
    onRoleAssignerPlaybackComplete() {
      this.cpuExpertMessages = this.reviewItem.anomalyAnalysis?.CpuExpert?.messages || []
      this.ioExpertMessages = this.reviewItem.anomalyAnalysis?.IoExpert?.messages || []
      this.memoryExpertMessages = this.reviewItem.anomalyAnalysis?.MemoryExpert?.messages || []
      this.networkExpertMessages = this.reviewItem.anomalyAnalysis?.NetworkExpert?.messages || []
      this.expertCount += this.cpuExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.ioExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.memoryExpertMessages.length > 0 ? 1 : 0
      this.expertCount += this.networkExpertMessages.length > 0 ? 1 : 0
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
      this.report = this.reviewItem.report || ''
    },
    getAlertHistoryDetail(item, callback) {
      this.roleAssignerMessages = []
      this.cpuExpertMessages = []
      this.ioExpertMessages = []
      this.memoryExpertMessages = []
      this.networkExpertMessages = []
      this.brainstormingMessages = []
      alertHistoryDetail({ file: item.file_name }).then(res => {
        this.reviewItem = res.data
        this.roleAssignerMessages = this.reviewItem.anomalyAnalysis.RoleAssigner.messages || []
        if (callback) {
          callback()
        }
      }).finally(() => {
        this.reviewLoading = false
      })
    },
    onReportClick(item) {
      this.reportDrawer = true
      this.getAlertHistoryDetail(item, () => {
        this.report = this.reviewItem.report || ''
      })
    },
    onStepClick(activeName) {
      console.log('======onStepClick==========:', activeName)
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
  line-height: 20px;
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
  height: 60px;
  flex-shrink: 0;
  border-bottom: 1px solid #f2f2f2;
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
