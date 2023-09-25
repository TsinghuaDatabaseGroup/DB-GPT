<template>
  <div class="c-flex-column c-relative" style="width: 100%; height: 100%;">
    <div id="scroll-container" class="scroll-container c-relative">
      <div
        class="message-header c-relative c-flex-row c-align-items-center"
        :style="hire ? 'background-color: #67C23A;' : 'background-color: RGBA(225, 243, 216, 1.00);'"
      >
        <img v-if="sender === 'Chief DBA'" src="@/assets/dba_robot.webp" class="face">
        <img v-if="sender === 'CPU Agent'" src="@/assets/cpu_robot.webp" class="face">
        <img v-if="sender === 'Memory Agent'" src="@/assets/mem_robot.webp" class="face">
        <img v-if="sender === 'IO Agent'" src="@/assets/io_robot.webp" class="face">
        <img v-if="sender === 'Network Agent'" src="@/assets/net_robot.webp" class="face">
        <span style="font-size: 16px; color: #FFFFFF; margin-left: 10px">{{ sender }}</span>
      </div>
      <template v-if="hire">
        <div v-for="(item, index) in messages" :key="index">
          <div class="text-item c-flex-row left">
            <div v-if="!item.loading" class="c-flex-column">
              <span style="font-size: 12px; color: #333333; margin-bottom: 5px">
                <span style="margin-left: 5px; color: #666666">{{ item.time }}</span>
              </span>
              <template v-if="item.type === 'message'">
                <div class="content c-flex-column">
                  <span style="font-size: 14px">{{ item.content.diagnose }}</span>
                </div>
                <div
                  v-if="isNotEmpty(item.content.solution)"
                  class="content c-flex-column"
                  style="background: rgba(103, 194, 58, 0.03); color: #ffffff"
                >
                  <span class="c-flex-column" style="color: RGBA(43, 127, 1, 0.8); margin: 10px 0">
                    <span style="color: RGBA(43, 127, 1, 1.00)">Matched Solution：</span>
                    <span v-for="(solu, soluIndex) in item.content.solution" :key="soluIndex">
                      {{ solu }}
                    </span>
                  </span>
                </div>
                <div v-if="item.content.knowledge && item.content.knowledge.trim()" class="content c-flex-column" style="background: RGBA(230, 162, 60, 0.03)">
                  <span class="c-flex-column" style="color: RGBA(230, 162, 60, 0.8); padding: 5px 0;">
                    <span style="color: RGBA(230, 162, 60, 1)">Matched Knowledge：</span>
                    <span>{{ item.content.knowledge || '' }}</span>
                  </span>
                </div>
              </template>
              <template v-else>
                <div class="content c-flex-column">
                  <span style="font-size: 14px">{{ item.content }}</span>
                </div>
              </template>
            </div>
            <div v-else>
              <div class="content c-flex-row c-justify-content-left" style="padding: 10px 40px 10px 20px">
                <i class="el-icon-loading" style="font-size: 20px; color: #000000" />
              </div>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="c-flex-column c-align-items-center c-justify-content-center" style="height: 60%;">
          <span style="font-size: 14px; color: #999999;">未被雇佣</span>
        </div>
      </template>
      <div class="item-space" />
    </div>
  </div>
</template>

<script>
import { parseTime } from '@/utils'

export default {
  name: 'OneChat',
  props: {
    messages: {
      type: Array,
      required: true,
      default: function() {
        return []
      }
    },
    sender: {
      type: String,
      required: true,
      default: ''
    },
    hire: {
      type: Boolean,
      required: true,
      default: false
    }
  },
  data() {
    return {
      chats: []
    }
  },
  methods: {
    parseTime(value) {
      return parseTime(value, '{m}-{d}')
    },
    isNotEmpty(arr) {
      return arr && arr.length > 0 && arr.some(element => element.trim() !== '')
    },
    // 初始化滚动
    initScrollBar() {
      this.$nextTick(() => {
        var container = this.$el.querySelector('.scroll-container')
        container.scrollTop = container.scrollHeight
      })
    }
  }
}
</script>

<style lang="scss" scoped>

.bottom-input-container {
  background: #ffffff;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  position: absolute;
}

.message-header {
  position: sticky;
  top: 0;
  width: 100%;
  background-color: #67C23A;
  z-index: 10;
  padding: 5px 10px
}

.scroll-container {
  transition: all 0.1s ease;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding-bottom: 20px;
  width: 100%;
  height: 100%;

  .item-space {
    height: 15px;
  }

  .time {
    color: #666;
    font-size: 12px;
    text-align: center;
    margin-bottom: 10px;
  }

  .time-item {
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    font-size: 15px;
    color: #9d9d9d;
  }

  .face {
    width: 40px;
    height: 40px;
    border-radius: 40px;
    margin-right: 7px;
  }

  .text-item {
    margin: 20px 10px;
    align-items: flex-start;
    justify-content: flex-start;

    .content {
      color: #333333;
      font-size: 14px;
      min-height: 20px;
      border-radius: 20px;
      padding: 6px 12px;
      line-height: 20px;
      background-color: #ffffff;
      word-break: break-all;
      word-wrap: break-word;
      position: relative;
    }
  }
}
</style>

