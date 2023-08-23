<template>
  <div class="c-flex-row c-align-items-center c-justify-content-between" style="height: calc(100vh - 80px)">
    <PgsqlDashboard class="c-shaow-card" style="width: 60%; height: 100%" />
    <div class="c-shaow-card c-flex-column" style="width: 40%; height: 100%; margin-left: 20px">
      <iframe src="http://127.0.0.1:7860/" style="height: 100%; width: 100%" />
      <!--      <div class="c-flex-column" style="padding: 20px; box-shadow: 0 0 5px 5px rgba(0, 0, 0, 0.02);">-->
      <!--        <span style="color: #666666">请选择异常发生时间进行分析：</span>-->
      <!--        <div class="c-flex-row c-align-items-center" style="margin-top: 10px">-->
      <!--          <el-date-picker-->
      <!--            v-model="timeRange"-->
      <!--            style="width: 400px;"-->
      <!--            type="datetimerange"-->
      <!--            :picker-options="pickerOptions"-->
      <!--            range-separator="至"-->
      <!--            format="yyyy-MM-dd HH:mm:ss"-->
      <!--            value-format="timestamp"-->
      <!--            start-placeholder="开始日期"-->
      <!--            end-placeholder="结束日期"-->
      <!--            :clearable="false"-->
      <!--            :editable="false"-->
      <!--            @change="timeRangeOnChange"-->
      <!--          />-->
      <!--          <div-->
      <!--            class="u-text-center"-->
      <!--            style="background: #682FF9; border-radius: 5px; padding: 10px; color: #FFFFFF; flex-shrink: 0; margin-left: 10px; cursor: pointer"-->
      <!--            @click="onChatConfirm()"-->
      <!--          >-->
      <!--            分析-->
      <!--          </div>-->
      <!--        </div>-->
      <!--      </div>-->
      <!--      <Chat />-->
    </div>
  </div>
</template>

<script>

import PgsqlDashboard from '@/components/PgsqlDashboard'
// import Chat from '@/components/Chat'
import { pickerOptions } from '@/utils/date_time_picker_options'

export default {
  components: { PgsqlDashboard },
  filters: {},
  data() {
    return {
      timeRange: [],
      pickerOptions: pickerOptions
    }
  },
  watch: {},
  mounted() {
  },
  beforeDestroy() {},
  methods: {

    timeRangeOnChange() {
    }
  }
}
</script>

<style scoped>
.container >>> .el-collapse-item__header {
  background: #f9f9f9;
}
</style>

<style lang="scss" scoped>

.container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.status-card-container {
  margin: auto;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  overflow-x: auto;
}

.status-card {
  min-width: 80px;
  margin-right: 10px;
  display: flex;
  min-height: 50px;
  flex-direction: column;
  justify-content: flex-start;
}

.top-card-title {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  text-align: center;
  height: 20px;
}

.top-card-detail {
  color: rgba(0, 0, 0, 0.85);
  font-weight: bolder;
  font-size: 18px;
  margin-top: 5px;
  text-align: center;
}

.card-header-title {
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
  white-space: nowrap;
  word-break: break-all;
  font-size: 18px;
}

.el-divider--horizontal {
  margin: 20px 0;
}

.el-col-5 {
  width: 20%;
}

.nineGridContainer {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 相当于 1fr 1fr 1fr */
  grid-gap: 10px; /* grid-column-gap 和 grid-row-gap的简写 */
  grid-auto-flow: row;

  .nineGrid {
    background-color: #FFFFFF;
  }

  margin-top: 20px;
}

.mysqlLineChart {
  width: 100%;
  height: 200px;
}

.detectorDiagnosticChart {
  width: 800px;
  height: 300px;
}

</style>
