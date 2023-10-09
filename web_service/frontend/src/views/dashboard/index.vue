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
          <el-button type="success" plain size="mini" style="margin-right: 10px" @click="onReviewClick(item)">回放</el-button>
          <el-button type="warning" plain size="mini" @click="onReportClick(item)">报告</el-button>
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
          <el-step title="异常分析" style="cursor: pointer" @click.n.native="onStepClick(0)" />
          <el-step title="圆桌讨论" style="cursor: pointer" @click.n.native="onStepClick(1)" />
          <el-step title="报告展示" style="cursor: pointer" @click.n.native="onStepClick(2)" />
        </el-steps>

        <transition name="fade">
          <div
            ref="setpScrollDiv"
            class="c-relative c-flex-column"
            style="height: calc(199 - 60px); overflow-y: auto; margin: 10px 0"
            @scroll="stepScrollEvent"
          >
            <div class="review-step">
              <div style="height: 40px; line-height: 40px; color: #666666;">
                DBA收到异常提醒后，会针对该异常进行分析，进而分配任务给不同的同事，接收到任务的同事会先独立进行分析。
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
                    sender="CpuExpert"
                    :hire="true"
                    class="chat-container"
                    :messages="memoryExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                  />
                  <OneChat
                    v-if="networkExpertMessages.length > 0"
                    sender="CpuExpert"
                    :hire="true"
                    class="chat-container"
                    :messages="networkExpertMessages"
                    style="height: 100%; margin-left: 20px; flex: 1 1 50%;"
                  />
                </div>
              </div>
            </div>

            <div class="review-step">
              <span style="height: 40px; line-height: 40px; color: #666666; margin: 10px 0">
                接收任务的同事独立进行异常分析后，会加入群组，进行圆桌讨论。
              </span>
              <Chat
                class="chat-container"
                :messages="brainstormingMessages"
                style="height: calc(100% - 40px); width: 100%; padding: 0"
              />
            </div>

            <div class="review-step">
              <span style="height: 40px; line-height: 40px; color: #666666">圆桌讨论后，DBA会将讨论结果汇总，出具异常分析诊断报告。</span>
              <VueMarkdown style="height: calc(100% - 40px); width: 100%; padding: 0" :source="report" />
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
      <div class="c-relative c-flex-column" style="overflow: scroll; height: calc(100% - 40px);">
        <VueMarkdown
          style="height: 100%; width: 100%; padding: 20px;"
          theme="light"
          :source="report"
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
import VueMarkdown from 'vue-markdown'
import hljs from 'highlight.js'

export default {
  filters: {},
  components: { OneChat, Chat, VueMarkdown },
  data() {
    return {
      timeRange: [],
      messages: [],
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
    hljs.highlightAll()
  },
  beforeDestroy() {
  },
  methods: {
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
.container >>> .el-collapse-item__header {
  background: #f9f9f9;
  width: 100vw;
}

.el-input__inner {
  border-radius: 20px;
}

.el-input--suffix .el-input__inner {
  padding-right: 10px;
}

.el-collapse-item__content {
  padding-bottom: 0;
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

.el-collapse-item__header {
  border-bottom: none;
}

.el-collapse-item__wrap {
  border-bottom: none;
}

.el-collapse {
  border: none;
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
