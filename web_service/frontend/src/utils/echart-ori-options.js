export const lineChartOption = {
  title: { show: true },
  grid: {
    left: 80,
    top: 60,
    bottom: 30,
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
  color: ['#1890FF', '#FFFF00', '#975FE4', ['#FE2E2E', '#01DF01', '#FFFF00']],
  legend: {
    data: [],
    bottom: 0,
    icon: 'pin',
    padding: 2,
    itemWidth: 10,
    itemHeight: 2,
    itemGap: 5,
    align: 'left',
    textStyle: {
      fontSize: 12
    }
  },
  xAxis: {
    splitArea: {
      show: true,
      interval: 0,
      areaStyle: {
        color: ['rgba(0, 0, 0, 0)']
      }
    },
    type: 'category',
    boundaryGap: false,
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
    axisLine: {
      show: false
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

