<template>
  <div class="c-flex-column" style=" width: 100%;">
    <el-form
      ref="form"
      class="c-shaow-card"
      :inline="true"
      label-position="left"
      size="mini"
      style="padding-top: 20px; padding-left: 20px; margin: 0 20px; border-radius: 80px!important;"
    >

      <el-form-item :label="$t('queryTimeTip') + ':'">
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

    <div class="c-flex c-flex-column" style="height: calc(100vh - 120px); overflow-y: auto; margin: 10px 0; padding: 0 20px">
      <div v-for="(item, index) in historyMessages" :key="index" class="diagnose-item c-flex-row c-align-items-center c-justify-content-between">
        <div class="title">{{ item.title }}</div>
        <div class="c-flex-row c-align-items-center">
          <el-button type="success" plain size="mini" style="margin-right: 10px" @click="onReviewClick(item)">{{ $t('playbackButton') }}</el-button>
          <el-button type="warning" plain size="mini" @click="onReportClick(item)">{{ $t('reportButton') }}</el-button>
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
              <div style="height: 40px; line-height: 40px; color: #333333; font-weight: bold">
                1.{{ $t('setpTip1') }}
              </div>
              <div class="c-flex-row c-align-items-center" style="height: calc(100% - 40px)">
                <OneChat
                  v-if="reviewItem['anomalyAnalysis']"
                  class="chat-container"
                  sender="RoleAssigner"
                  :hire="true"
                  :messages="reviewItem.anomalyAnalysis.RoleAssigner.messages"
                  style="height: 100%; width: 30%;"
                />
                <div class="c-flex-row" style="width: 70%; height: 100%;">
                  <OneChat
                    v-if="cpuExpertMessages.length > 0"
                    sender="CpuExpert"
                    :hire="true"
                    class="chat-container"
                    :messages="cpuExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                  />
                  <OneChat
                    v-if="ioExpertMessages.length > 0"
                    sender="IoExpert"
                    :hire="true"
                    class="chat-container"
                    :messages="ioExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                  />
                  <OneChat
                    v-if="memoryExpertMessages.length > 0"
                    sender="MemoryExpert"
                    :hire="true"
                    class="chat-container"
                    :messages="memoryExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                  />
                  <OneChat
                    v-if="networkExpertMessages.length > 0"
                    sender="NetworkExpert"
                    :hire="true"
                    class="chat-container"
                    :messages="networkExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                  />
                </div>
              </div>
            </div>

            <div class="review-step">
              <span style="height: 40px; line-height: 40px; color: #333333; font-weight: bold; margin: 10px 0">
                2.{{ $t('setpTip2') }}
              </span>
              <Chat
                class="chat-container"
                :messages="brainstormingMessages"
                style="height: calc(100% - 40px); width: 100%; padding: 0"
              />
            </div>

            <div class="review-step">
              <span style="height: 40px; line-height: 40px; color: #333333; font-weight: bold;">3.{{ $t('setpTip3') }}</span>
              <div style="width: 100%; padding: 10px;" v-html="md.render(report)" />
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
          style="height: 100%; width: 100%; padding: 20px;"
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
      md: new MarkdownIt()
        .set({ html: true, breaks: true, typographer: true, linkify: true })
        .set({ highlight: function(code) {
          return '<pre class="hljs"><code>' +
              hljs.highlight(code, { language: 'python', ignoreIllegals: true }).value +
              '</code></pre>'
        } }),
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
      reportDrawer: false
    }
  },
  watch: {},
  mounted() {
    // this.messages = JSON.parse(localStorage.getItem(MESSAGEKEY) || '[]')
    // this.getRobotIntro()
    this.getAlertHistories()
  },
  beforeDestroy() {
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
    getAlertHistoryDetail(item) {
      this.cpuExpertMessages = []
      this.ioExpertMessages = []
      this.memoryExpertMessages = []
      this.networkExpertMessages = []
      this.brainstormingMessages = []
      alertHistoryDetail({ file: item.file_name }).then(res => {
        this.reviewItem = res.data
        this.cpuExpertMessages = this.reviewItem.anomalyAnalysis?.CpuExpert?.messages || []
        this.ioExpertMessages = this.reviewItem.anomalyAnalysis?.IoExpert?.messages || []
        this.memoryExpertMessages = this.reviewItem.anomalyAnalysis?.MemoryExpert?.messages || []
        this.networkExpertMessages = this.reviewItem.anomalyAnalysis?.NetworkExpert?.messages || []
        this.brainstormingMessages = this.reviewItem.brainstorming?.messages || []
        this.report = this.reviewItem.report || ''
      }).finally(() => {
        this.reviewLoading = false
      })
    },
    onReportClick(item) {
      this.reportDrawer = true
      this.getAlertHistoryDetail(item)
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
    color: #000000;
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
