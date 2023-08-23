<template>
  <div v-loading="loading" class="container">

    <el-form ref="form" :inline="true" label-position="left" size="mini">

      <el-form-item label="Instance:">
        <el-select
          v-model="dbSelectCondition"
          style="min-width: 120px"
          clearable
          filterable
          placeholder="请选择"
        >
          <el-option
            v-for="item in dbSelecteds"
            :key="item.instance"
            :label="item.instance"
            :value="item.instance"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="查询时间:">
        <el-date-picker
          v-model="timeRange"
          type="datetimerange"
          :picker-options="pickerOptions"
          range-separator="至"
          format="yyyy-MM-dd HH:mm:ss"
          value-format="timestamp"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :clearable="false"
          :editable="false"
          @change="timeRangeOnChange"
        />
      </el-form-item>

      <el-form-item label="查询间隔:">
        <el-select
          v-model="timeSelectCondition"
          style="min-width: 80px"
          clearable
          filterable
          placeholder="请选择"
          @change="reloadRefreshTimer"
        >
          <el-option
            v-for="item in timeSelecteds"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="自动刷新:">
        <el-switch
          v-model="autoRefresh"
          active-color="#13ce66"
          inactive-color="#ff4949"
        />
      </el-form-item>

    </el-form>

    <el-card shadow="always" style="flex-shrink: 0">
      <div class="status-card-container">
        <div v-for="(item, index) in osStatus" :key="index" class="status-card">
          <div class="top-card-title">{{ item.label }}</div>
          <div class="top-card-detail">{{ item.value }}</div>
        </div>
      </div>
    </el-card>

    <div class="nineGridContainer" style="margin-top: 10px">
      <el-card class="nineGrid" shadow="always">
        <div class="card-header-title">Average CPU Usage</div>
        <el-divider />
        <lineChart class="lineChart" :chart-option="averageCPUUsageChartOption" />
      </el-card>

      <el-card class="nineGrid" shadow="always">
        <div class="card-header-title">Average Memory Usage</div>
        <el-divider />
        <lineChart class="lineChart" :chart-option="averageMemoryUsageChartOption" />
      </el-card>
      <el-card class="nineGrid" shadow="always">
        <div class="card-header-title">Open File Descriptors</div>
        <el-divider />
        <lineChart class="lineChart" :chart-option="openFileDescriptorsChartOption" />
      </el-card>

      <el-card class="nineGrid" shadow="always">
        <div class="card-header-title">Active sessions</div>
        <el-divider />
        <lineChart class="lineChart" :chart-option="activeSessionsChartOption" />
      </el-card>
      <el-card class="nineGrid" style="width: calc(200% + 10px)" shadow="always">
        <div class="card-header-title">Buffers (bgwriter)</div>
        <el-divider />
        <lineChart class="lineChart" :chart-option="buggersChartOption" />
      </el-card>
      <div />
      <el-card class="nineGrid" style="width: calc(200%)" shadow="always">
        <div class="card-header-title">Checkpoint Stats</div>
        <el-divider />
        <lineChart class="lineChart" :chart-option="checkpointStatsChartOption" />
      </el-card>
      <div />
    </div>

  </div>
</template>

<script>

import { query, query_range } from '@/api/prometheus'
import { bytesToSize, stringFoFixed2 } from '@/utils'
import lineChart from '@/components/echarts/vue-chart'
import { lineChartOption } from '@/utils/echart-ori-options'
import { pickerOptions } from '@/utils/date_time_picker_options'
import moment from 'moment'

export default {
  components: { lineChart },
  filters: {
    percentageFilter: function(value) {
      if (!value) {
        return ''
      }
      return Math.round(value * 100) / 100.0 + '%'
    }
  },
  data() {
    return {
      dbSelecteds: [],
      dbSelectCondition: undefined,
      collapseActiveNames: ['1'],
      timeSelecteds: [
        { label: '10s', value: '10s' },
        { label: '30s', value: '30s' },
        { label: '1m', value: '1m' },
        { label: '5m', value: '5m' }
      ],
      timeSelectedToMs: {
        '10s': 10000,
        '30s': 30000,
        '1m': 60000,
        '5m': 300000
      },
      pageSize: 8,
      pageIndex: 1,
      totalItems: 0,
      refreshTimer: undefined,
      timeSelectCondition: '1m',
      queryStep: '1m',
      pickerOptions: pickerOptions,
      timeRange: [],
      alarmHistoaryRecentlyData: [],
      alarmHistoaryRecentlyAllData: [],
      osStatus: [
        { label: 'Version', value: '' },
        { label: 'Current Fetch Data', value: '' },
        { label: 'Current Insert Data', value: '' },
        { label: 'Current Update Data', value: '' },
        { label: 'MAX Connections', value: '' }
      ],
      loading: false,
      autoRefresh: false,
      averageCPUUsageChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      averageMemoryUsageChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      openFileDescriptorsChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      activeSessionsChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      buggersChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      checkpointStatsChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      detectorDiagnosticChartOption: JSON.parse(JSON.stringify(lineChartOption))
    }
  },
  watch: {
    dbSelectCondition(value) {
      this.reloadRequest()
    },
    timeSelectCondition(value) {
      this.reloadRequest()
    }
  },
  mounted() {
    this.timeRange = [moment().add(-1, 'h').format('x'), moment().format('x')]
    this.chartOptionSeeting()
    this.nodesInfo()
  },
  beforeDestroy() {
    this.clearRefreshTimer()
  },
  methods: {
    chartOptionSeeting() {
      //  Average CPU UsageChart
      this.averageCPUUsageChartOption.tooltip.formatter = function(params, ticket, callback) {
        var result = params[0].axisValueLabel + '</br>'
        for (let i = 0; i < params.length; i++) {
          const param = params[i]
          result = result + `${param.marker}&nbsp${param.seriesName}:&nbsp ${stringFoFixed2(param.value[1] * 1000)}ms</br>`
        }
        setTimeout(function() {
          // 仅为了模拟异步回调
          callback(ticket, result)
        }, 100)
        return 'loading...'
      }
      this.averageCPUUsageChartOption.yAxis.axisLabel.formatter = function(value, index) {
        return stringFoFixed2(value * 1000) + 'ms'
      }
      this.averageCPUUsageChartOption.xAxis.type = 'time'
      this.averageCPUUsageChartOption.color = ['#00FFFF']
      this.averageCPUUsageChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.averageCPUUsageChartOption.legend.data = ['CPU Time']
      this.averageCPUUsageChartOption.series = [
        {
          name: 'CPU Time',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        }
      ]

      //  Average Memory Usage
      this.averageMemoryUsageChartOption.tooltip.formatter = function(params, ticket, callback) {
        var result = params[0].axisValueLabel + '</br>'
        for (let i = 0; i < params.length; i++) {
          const param = params[i]
          result = result + `${param.marker}&nbsp${param.seriesName}:&nbsp ${bytesToSize(param.value[1])}</br>`
        }
        setTimeout(function() {
          // 仅为了模拟异步回调
          callback(ticket, result)
        }, 100)
        return 'loading...'
      }
      this.averageMemoryUsageChartOption.yAxis.axisLabel.formatter = function(value, index) {
        return bytesToSize(value)
      }
      this.averageMemoryUsageChartOption.xAxis.type = 'time'
      this.averageMemoryUsageChartOption.color = ['#975FE4', '#01DF3A']
      this.averageMemoryUsageChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.averageMemoryUsageChartOption.legend.data = ['Resident Mem', 'Virtual Mem']
      this.averageMemoryUsageChartOption.series = [
        {
          name: 'Resident Mem',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'Virtual Mem',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        }
      ]

      //  Open File Descriptors
      this.openFileDescriptorsChartOption.tooltip.formatter = function(params, ticket, callback) {
        var result = params[0].axisValueLabel + '</br>'
        for (let i = 0; i < params.length; i++) {
          const param = params[i]
          result = result + `${param.marker}&nbsp${param.seriesName}:&nbsp ${stringFoFixed2(param.value[1])}</br>`
        }
        setTimeout(function() {
          // 仅为了模拟异步回调
          callback(ticket, result)
        }, 100)
        return 'loading...'
      }
      this.openFileDescriptorsChartOption.xAxis.type = 'time'
      this.openFileDescriptorsChartOption.color = ['#1890FF']
      this.openFileDescriptorsChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.openFileDescriptorsChartOption.legend.data = ['Open FD']
      this.openFileDescriptorsChartOption.series = [
        {
          name: 'Open FD',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false
        }
      ]

      // Active sessions
      this.activeSessionsChartOption.tooltip.formatter = function(params, ticket, callback) {
        var result = params[0].axisValueLabel + '</br>'
        for (let i = 0; i < params.length; i++) {
          const param = params[i]
          result = result + `${param.marker}&nbsp${param.seriesName}:&nbsp ${stringFoFixed2(param.value[1])}</br>`
        }
        setTimeout(function() {
          // 仅为了模拟异步回调
          callback(ticket, result)
        }, 100)
        return 'loading...'
      }
      this.activeSessionsChartOption.xAxis.type = 'time'
      this.activeSessionsChartOption.color = ['#01DF3A', '#FFFF00', '#1890FF']
      this.activeSessionsChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.activeSessionsChartOption.legend.data = ['dbmind']
      this.activeSessionsChartOption.series = [
        {
          name: 'dbmind',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        }
      ]

      // Buffers (bgwriter)
      this.buggersChartOption.tooltip.formatter = function(params, ticket, callback) {
        var result = params[0].axisValueLabel + '</br>'
        for (let i = 0; i < params.length; i++) {
          const param = params[i]
          result = result + `${param.marker}&nbsp${param.seriesName}:&nbsp ${stringFoFixed2(param.value[1])}</br>`
        }
        setTimeout(function() {
          // 仅为了模拟异步回调
          callback(ticket, result)
        }, 100)
        return 'loading...'
      }
      this.buggersChartOption.xAxis.type = 'time'
      this.buggersChartOption.color = ['#FE2E2E', '#00FFFF', '#1890FF']
      this.buggersChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.buggersChartOption.legend.data = ['buffers_backend', 'buffers_alloc', 'backend_fsync', 'buffers_checkpoint', 'buffers_clean']
      this.buggersChartOption.series = [
        {
          name: 'buffers_backend',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'buffers_alloc',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'backend_fsync',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'buffers_checkpoint',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'buffers_clean',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        }
      ]

      //  Checkpoint Stats
      this.checkpointStatsChartOption.tooltip.formatter = function(params, ticket, callback) {
        var result = params[0].axisValueLabel + '</br>'
        for (let i = 0; i < params.length; i++) {
          const param = params[i]
          result = result + `${param.marker}&nbsp${param.seriesName}:&nbsp ${stringFoFixed2(param.value[1] * 1000)}ms</br>`
        }
        setTimeout(function() {
          // 仅为了模拟异步回调
          callback(ticket, result)
        }, 100)
        return 'loading...'
      }
      this.checkpointStatsChartOption.yAxis.axisLabel.formatter = function(value, index) {
        return stringFoFixed2(value * 1000) + 'ms'
      }
      this.checkpointStatsChartOption.xAxis.type = 'time'
      this.checkpointStatsChartOption.color = ['#00FFFF']
      this.checkpointStatsChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.checkpointStatsChartOption.legend.data = ['write_time', 'sync_time']
      this.checkpointStatsChartOption.series = [
        {
          name: 'write_time',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'sync_time',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        }
      ]
    },
    startTimeFormatter(row, column) {
      return moment(row.last_begin_time).format('YYYY-MM-DD HH:mm:ss')
    },
    timeRangeOnChange() {
      if (this.timeRange && this.timeRange.length > 1) {
        this.reloadRequest()
      }
    },
    reloadRefreshTimer() {
      this.clearRefreshTimer()
      this.refreshTimer = setInterval(() => {
        if (this.autoRefresh) {
          this.timeRange = [moment().add(-1, 'h').format('x'), moment().format('x')]
          this.reloadRequest()
        }
      }, this.timeSelectedToMs[this.timeSelectCondition])
    },
    clearRefreshTimer() {
      clearInterval(this.refreshTimer)
      this.refreshTimer = null
    },
    nodesInfo() {
      query({ 'query': 'pg_exporter_last_scrape_duration_seconds', time: parseInt((new Date()).valueOf() / 1000) - 3000 }).then(res => {
        console.log(res.data)
        this.dbSelecteds = res.data.result.map(item => {
          return item.metric
        })
        this.dbSelectCondition = this.dbSelecteds[0].instance
      })
    },
    reloadRequest() {
      if (!this.dbSelectCondition) {
        return
      }

      this.queryRequest(`pg_static{release="", instance=~"${this.dbSelectCondition}"}`).then(res => {
        this.osStatus[0].value = res.metric?.short_version || 'No Data'
      })
      this.queryRequest(`SUM(pg_stat_database_tup_fetched{instance=~"${this.dbSelectCondition}"})`).then(res => {
        this.osStatus[1].value = res ? bytesToSize(res.value[1]) : 'No Data'
      })
      this.queryRequest(`SUM(pg_stat_database_tup_inserted{release="", instance=~"${this.dbSelectCondition}"})`).then(res => {
        this.osStatus[2].value = res ? bytesToSize(res.value[1]) : 'No Data'
      })

      this.queryRequest(`SUM(pg_stat_database_tup_updated{release="", instance=~"${this.dbSelectCondition}"})`).then(res => {
        this.osStatus[3].value = res ? bytesToSize(res.value[1]) : 'No Data'
      })

      this.queryRequest(`pg_settings_max_connections{release="", instance=~"${this.dbSelectCondition}"}`).then(res => {
        this.osStatus[4].value = res ? res.value[1] : 'No Data'
      })

      this.queryRangeRequest(`avg(rate(process_cpu_seconds_total{release="", instance="${this.dbSelectCondition}"}[${this.queryStep}]) * 1000)`).then(res => {
        this.averageCPUUsageChartOption.series[0].data = res
      })

      this.queryRangeRequest(`avg(rate(process_resident_memory_bytes{release="", instance="${this.dbSelectCondition}"}[${this.queryStep}]))`).then(res => {
        this.averageMemoryUsageChartOption.series[0].data = res
      })

      this.queryRangeRequest(`avg(rate(process_virtual_memory_bytes{release="", instance="${this.dbSelectCondition}"}[${this.queryStep}]))`).then(res => {
        this.averageMemoryUsageChartOption.series[1].data = res
      })

      this.queryRangeRequest(`process_open_fds{release="", instance="${this.dbSelectCondition}"}`).then(res => {
        this.openFileDescriptorsChartOption.series[0].data = res
      })

      this.queryRangeRequest(`pg_stat_activity_count{instance=~"${this.dbSelectCondition}", state="active"} !=0`).then(res => {
        this.activeSessionsChartOption.series[0].data = res
      })

      this.queryRangeRequest(`irate(pg_stat_bgwriter_buffers_backend{instance="${this.dbSelectCondition}"}[${this.queryStep}])`).then(res => {
        this.buggersChartOption.series[0].data = res
      })

      this.queryRangeRequest(`irate(pg_stat_bgwriter_buffers_alloc{instance="${this.dbSelectCondition}"}[${this.queryStep}])`).then(res => {
        this.buggersChartOption.series[1].data = res
      })

      this.queryRangeRequest(`irate(pg_stat_bgwriter_buffers_backend_fsync{instance="${this.dbSelectCondition}"}[${this.queryStep}])`).then(res => {
        this.buggersChartOption.series[2].data = res
      })

      this.queryRangeRequest(`irate(pg_stat_bgwriter_buffers_checkpoint{instance="${this.dbSelectCondition}"}[${this.queryStep}])`).then(res => {
        this.buggersChartOption.series[3].data = res
      })

      this.queryRangeRequest(`irate(pg_stat_bgwriter_buffers_clean{instance="${this.dbSelectCondition}"}[${this.queryStep}])`).then(res => {
        this.buggersChartOption.series[4].data = res
      })

      this.queryRangeRequest(`irate(pg_stat_bgwriter_checkpoint_write_time{instance="${this.dbSelectCondition}"}[${this.queryStep}])`).then(res => {
        this.checkpointStatsChartOption.series[0].data = res
      })

      this.queryRangeRequest(`irate(pg_stat_bgwriter_checkpoint_sync_time{instance="${this.dbSelectCondition}"}[${this.queryStep}])`).then(res => {
        this.checkpointStatsChartOption.series[1].data = res
      })
    },
    queryRequest(queryUrl) {
      return new Promise((resolve, reject) => {
        query({ query: queryUrl }).then(res => {
          const data = res.data
          if (data && data.result && data.result.length > 0 && data.result[0].value) {
            resolve(data.result[0])
          } else {
            resolve(undefined)
          }
        })
      })
    },
    queryRangeRequest(queryUrl, original = false) {
      return new Promise((resolve, reject) => {
        query_range({
          query: queryUrl,
          start: this.timeRange[0] ? this.timeRange[0] / 1000 : (new Date()).valueOf() / 1000 - 3600 * 24,
          end: this.timeRange[1] ? this.timeRange[1] / 1000 : (new Date()).valueOf() / 1000,
          step: 60
        }).then(res => {
          const data = res.data
          if (data && data.result && data.result.length > 0) {
            if (original) {
              resolve(res)
            } else {
              if (data.result[0].values.length > 0) {
                const values = data.result[0].values
                var results = []
                for (let i = 0; i < values.length; i++) {
                  const value = values[i]
                  results.push([value[0] * 1000, value[1]])
                }
                resolve(results)
              } else {
                resolve(undefined)
              }
            }
          } else {
            resolve(undefined)
          }
        })
      })
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
  padding: 20px;
  height: 100%;
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
  position: relative;
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 相当于 1fr 1fr 1fr */
  grid-gap: 10px; /* grid-column-gap 和 grid-row-gap的简写 */
  grid-auto-flow: row;
  overflow-y: scroll;
  .nineGrid {
    background-color: #FFFFFF;
    height: 300px;
  }
  margin-top: 20px;
}

.lineChart {
  width: 100%;
  height: 200px;
}

</style>
