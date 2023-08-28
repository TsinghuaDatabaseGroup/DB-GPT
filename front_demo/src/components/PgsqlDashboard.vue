<template>
  <div v-loading="loading" class="container">

    <el-form
      ref="form"
      class="c-shaow-card"
      :inline="true"
      label-position="left"
      size="mini"
      style="padding-top: 20px; margin: 0 20px; padding-left: 20px; margin-bottom: 20px"
    >

      <el-form-item :label="$t('refreshTip') + ':'">
        <el-switch
          v-model="autoRefresh"
          active-color="#13ce66"
          inactive-color="#ff4949"
        />
      </el-form-item>

      <el-form-item :label="$t('queryTimeTip') + ':'">
        <el-date-picker
          v-model="timeRange"
          style="width: 340px"
          type="datetimerange"
          :picker-options="pickerOptions"
          range-separator="-"
          format="yyyy-MM-dd HH:mm:ss"
          value-format="timestamp"
          :start-placeholder="$t('timeStartTip')"
          :end-placeholder="$t('timeEndTip')"
          :clearable="false"
          :disabled="autoRefresh"
          @change="timeRangeOnChange"
        />
      </el-form-item>

    </el-form>

    <div style="width: 100%; overflow-y: scroll">

      <div class="status-card-container" style="flex-shrink: 0; margin: 20px; margin-top: 0">
        <div v-for="(item, index) in osStatus" :key="index" class="status-card c-shaow-card">
          <div class="top-card-title">{{ item.label }}</div>
          <div class="top-card-detail">{{ item.value }}</div>
        </div>
      </div>

      <el-card class="nineGrid" style="width: calc(100% - 40px); margin: 0 20px; flex-shrink: 0" shadow="never">
        <div class="card-header-title">CPU Usage</div>
        <el-divider />
        <lineChart class="lineChart" :chart-option="cpuUsageRateChartOption" />
      </el-card>

      <div class="status-card-container" style="flex-shrink: 0; margin: 20px">
        <div v-for="(item, index) in nodeStatus" :key="index" class="status-card c-shaow-card" style="width: calc(100%/7 - 20px);">
          <div class="top-card-title">{{ item.label }}</div>
          <div class="top-card-detail">{{ item.value }}</div>
        </div>
      </div>

      <div class="nineGridContainer">
        <el-card class="nineGrid" shadow="never">
          <div class="card-header-title">System Average Load</div>
          <el-divider />
          <lineChart class="lineChart" :chart-option="avgLoadChartOption" />
        </el-card>

        <el-card class="nineGrid" shadow="never">
          <div class="card-header-title">Memory Usage</div>
          <el-divider />
          <lineChart class="lineChart" :chart-option="memoryChartOption" />
        </el-card>

        <el-card class="nineGrid" shadow="never">
          <div class="card-header-title">Open File Descriptors</div>
          <el-divider />
          <lineChart class="lineChart" :chart-option="openFileDescriptorsChartOption" />
        </el-card>

        <el-card class="nineGrid" shadow="never">
          <div class="card-header-title">Active sessions</div>
          <el-divider />
          <lineChart class="lineChart" :chart-option="activeSessionsChartOption" />
        </el-card>

        <el-card class="nineGrid" style="width: calc(200% + 10px)" shadow="never">
          <div class="card-header-title">Buffers (bgwriter)</div>
          <el-divider />
          <lineChart class="lineChart" :chart-option="buggersChartOption" />
        </el-card>
        <div />
        <el-card class="nineGrid" style="width: calc(200% + 10px)" shadow="never">
          <div class="card-header-title">Checkpoint Stats</div>
          <el-divider />
          <lineChart class="lineChart" :chart-option="checkpointStatsChartOption" />
        </el-card>
        <div />
      </div>
    </div>
  </div>
</template>

<script>

import { query, query_range } from '@/api/prometheus'
import { bytesToSize, bytesToSizeSecondsRate, stringFoFixed2, stringToPercent } from '@/utils'
import lineChart from '@/components/echarts/vue-chart'
import { lineChartOption } from '@/utils/echart-ori-options'
import moment from 'moment'
import { instances } from '@/api/api'

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
      nodeSelectCondition: '',
      dbSelectCondition: '',
      prometheusApiUrl: '',
      timeSelecteds: [
        { label: '10s', value: '10s' },
        { label: '30s', value: '30s' },
        { label: '1m', value: '1m' },
        { label: '5m', value: '5m' }
      ],
      refreshTimer: undefined,
      refreshTimestamp: 3000,
      queryStep: '1m',
      pickerOptions: [],
      timeRange: [],
      alarmHistoaryRecentlyData: [],
      alarmHistoaryRecentlyAllData: [],
      osStatus: [
        { label: 'Postgres Version', value: '' },
        { label: 'Current Fetch Data', value: '' },
        { label: 'Current Insert Data', value: '' },
        { label: 'Current Update Data', value: '' },
        { label: 'MAX Connections', value: '' }
      ],
      nodeStatus: [
        { label: 'CPU Cores', value: '' },
        { label: 'Total Memory', value: '' },
        { label: 'CPU Usage', value: '' },
        { label: 'Mem Usage', value: '' },
        { label: 'Disk Usage', value: '' },
        { label: 'TCP_tw', value: '' },
        { label: 'Disk Read', value: '' }
      ],
      loading: false,
      autoRefresh: true,
      cpuUsageRateChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      memoryChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      openFileDescriptorsChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      activeSessionsChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      buggersChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      checkpointStatsChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      detectorDiagnosticChartOption: JSON.parse(JSON.stringify(lineChartOption)),
      avgLoadChartOption: JSON.parse(JSON.stringify(lineChartOption))
    }
  },
  watch: {
    dbSelectCondition(value) {
      this.reloadRequest()
    },
    autoRefresh: {
      handler(value) {
        if (value) {
          this.reloadRefreshTimer()
        } else {
          this.clearRefreshTimer()
        }
      },
      deep: true,
      immediate: true
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
      this.cpuUsageRateChartOption.xAxis.type = 'time'
      this.cpuUsageRateChartOption.color = ['#1890FF', '#00FFFF', '#FFFF00', '#975FE4']
      this.cpuUsageRateChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.cpuUsageRateChartOption.yAxis.axisLabel.formatter = '{value} %'
      this.cpuUsageRateChartOption.legend.data = ['idle rate', 'user rate', 'system rate', 'iowait rate']
      this.cpuUsageRateChartOption.series = [
        {
          name: 'idle rate',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'user rate',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'system rate',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'iowait rate',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        }
      ]

      //  Memory Usage
      this.memoryChartOption.tooltip.formatter = function(params, ticket, callback) {
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
      this.memoryChartOption.xAxis.type = 'time'
      this.memoryChartOption.grid.left = 60
      this.memoryChartOption.color = ['#FE2E2E', '#01DF01', '#1890FF']
      this.memoryChartOption.yAxis.axisLabel.formatter = function(value, index) {
        return bytesToSize(value)
      }
      this.memoryChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.memoryChartOption.legend.data = ['Total Memory', 'Available Memory', 'Used Memory']
      this.memoryChartOption.series = [
        {
          name: 'Total Memory',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'Available Memory',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: 'Used Memory',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        }
      ]

      //  系统平均负载
      this.avgLoadChartOption.xAxis.type = 'time'
      this.avgLoadChartOption.grid.left = 60
      this.avgLoadChartOption.color = ['#FE2E2E', '#01DF3A', '#FFFF00']
      this.avgLoadChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.avgLoadChartOption.legend.data = ['15M', '5M', '1M']
      this.avgLoadChartOption.series = [
        {
          name: '15M',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: '5M',
          data: [],
          type: 'line',
          smooth: true,
          showSymbol: false,
          areaStyle: { type: 'default' }
        },
        {
          name: '1M',
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
          showSymbol: false,
          areaStyle: { type: 'default' }
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
      this.activeSessionsChartOption.color = ['#2B9C0F']
      this.activeSessionsChartOption.xAxis.axisLabel.formatter = '{HH}:{mm}'
      this.activeSessionsChartOption.legend.data = []
      this.activeSessionsChartOption.series = [
        {
          name: '',
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
        this.timeRange = [moment().add(-1, 'h').format('x'), moment().format('x')]
        this.reloadRequest()
      }, this.refreshTimestamp)
    },
    clearRefreshTimer() {
      clearInterval(this.refreshTimer)
      this.refreshTimer = null
    },
    nodesInfo() {
      instances({}).then(res => {
        this.prometheusApiUrl = res.data.url
        this.dbSelectCondition = res.data.postgresql
        this.nodeSelectCondition = res.data.node
      })
    },
    reloadRequest() {
      if (!this.nodeSelectCondition || !this.dbSelectCondition || !this.prometheusApiUrl) {
        return
      }

      this.queryRequest(`pg_static{release="", instance=~"${this.dbSelectCondition}"}`).then(res => {
        this.osStatus[0].value = (res.metric?.short_version || 'No Data')
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

      this.queryRequest(`count(node_cpu_seconds_total{origin_prometheus=~"",job=~"node", mode='system', instance=~"${this.nodeSelectCondition}"})`).then(res => {
        this.nodeStatus[0].value = res.value[1]
      })
      this.queryRequest(`node_memory_MemTotal_bytes{origin_prometheus=~"",job=~"node", instance=~"${this.nodeSelectCondition}"} - 0`).then(res => {
        this.nodeStatus[1].value = bytesToSize(res.value[1]) || ''
      })

      this.queryRequest(`(1 - avg(rate(node_cpu_seconds_total{origin_prometheus=~"",job=~"node",mode="idle", instance=~"${this.nodeSelectCondition}"}[${this.queryStep}]))) * 100`).then(res => {
        this.nodeStatus[2].value = stringToPercent(res.value[1])
      })
      this.queryRequest(`(1 - (node_memory_MemAvailable_bytes{origin_prometheus=~"",job=~"node"} / (node_memory_MemTotal_bytes{origin_prometheus=~"",job=~"node", instance=~"${this.nodeSelectCondition}"})))* 100`).then(res => {
        this.nodeStatus[3].value = stringToPercent(res.value[1])
      })
      this.queryRequest(`max((node_filesystem_size_bytes{origin_prometheus=~"",job=~"node",instance=~"${this.nodeSelectCondition}",fstype=~"ext.?|xfs"}-node_filesystem_free_bytes{origin_prometheus=~"",job=~"node",instance=~"${this.nodeSelectCondition}",fstype=~"ext.?|xfs"}) *100/(node_filesystem_avail_bytes {origin_prometheus=~"",job=~"node",instance=~"${this.nodeSelectCondition}",fstype=~"ext.?|xfs"}+(node_filesystem_size_bytes{origin_prometheus=~"",job=~"node",instance=~"${this.nodeSelectCondition}",fstype=~"ext.?|xfs"}-node_filesystem_free_bytes{origin_prometheus=~"",job=~"node",instance=~"${this.nodeSelectCondition}",fstype=~"ext.?|xfs"})))by(instance)`).then(res => {
        this.nodeStatus[4].value = stringToPercent(res.value[1])
      })

      this.queryRequest(`node_sockstat_TCP_tw{origin_prometheus=~"",job=~"node",instance=~"${this.nodeSelectCondition}"} - 0`).then(res => {
        this.nodeStatus[5].value = res.value[1]
      })
      this.queryRequest(`max(rate(node_disk_read_bytes_total{origin_prometheus=~"",job=~"node",instance=~"${this.nodeSelectCondition}"}[${this.queryStep}])) by (instance)`).then(res => {
        this.nodeStatus[6].value = bytesToSizeSecondsRate(res.value[1])
      })

      this.queryRangeRequest(`(1 - avg(rate(node_cpu_seconds_total{instance=~"${this.nodeSelectCondition}",mode="idle"}[${this.queryStep}])) by (instance))*100`).then(res => {
        this.cpuUsageRateChartOption.series[0].data = res
      })
      this.queryRangeRequest(`avg(rate(node_cpu_seconds_total{instance=~"${this.nodeSelectCondition}",mode="user"}[${this.queryStep}])) by (instance) *100`).then(res => {
        this.cpuUsageRateChartOption.series[1].data = res
      })
      this.queryRangeRequest(`avg(rate(node_cpu_seconds_total{instance=~"${this.nodeSelectCondition}",mode="system"}[${this.queryStep}])) by (instance) *100`).then(res => {
        this.cpuUsageRateChartOption.series[2].data = res
      })
      this.queryRangeRequest(`avg(rate(node_cpu_seconds_total{instance=~"${this.nodeSelectCondition}",mode="iowait"}[${this.queryStep}])) by (instance) *100`).then(res => {
        this.cpuUsageRateChartOption.series[3].data = res
      })

      this.queryRangeRequest(`node_memory_MemTotal_bytes{instance=~"${this.nodeSelectCondition}"}`).then(res => {
        this.memoryChartOption.series[0].data = res
      })
      this.queryRangeRequest(`node_memory_MemAvailable_bytes{instance=~"${this.nodeSelectCondition}"}`).then(res => {
        this.memoryChartOption.series[1].data = res
      })
      this.queryRangeRequest(`node_memory_MemTotal_bytes{instance=~"${this.nodeSelectCondition}"} - node_memory_MemAvailable_bytes{instance=~"${this.nodeSelectCondition}"}`).then(res => {
        this.memoryChartOption.series[2].data = res
      })

      this.queryRangeRequest(`node_load15{instance=~"${this.nodeSelectCondition}"}`).then(res => {
        this.avgLoadChartOption.series[0].data = res
      })
      this.queryRangeRequest(`node_load5{instance=~"${this.nodeSelectCondition}"}`).then(res => {
        this.avgLoadChartOption.series[1].data = res
      })
      this.queryRangeRequest(`node_load1{instance=~"${this.nodeSelectCondition}"}`).then(res => {
        this.avgLoadChartOption.series[2].data = res
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
        query(this.prometheusApiUrl, { query: queryUrl }).then(res => {
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
        query_range(this.prometheusApiUrl, {
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
.el-input__inner {
  border-radius: 20px;
}
</style>

<style lang="scss" scoped>

.container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.status-card-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: calc(100% - 40px);
  margin: 20px 0;
}

.status-card {
  padding: 20px;
  width: calc(20% - 20px);
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
  margin: 0 20px;
}

.nineGrid {
  background-color: #FFFFFF;
  height: 300px;
  border-radius: 20px;
  box-shadow: 0 0 3px 3px rgba(0, 0, 0, 0.03);
  border: none;
  pointer-events: none;
}

.lineChart {
  width: 100%;
  height: 200px;
}

</style>
