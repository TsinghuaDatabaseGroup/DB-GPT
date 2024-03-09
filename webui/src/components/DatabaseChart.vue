<template>
  <v-chart style="width: 100%; height: 200px; border-radius: 8px; overflow: hidden" :option="option" autoresize />
</template>

<script setup>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import {
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
} from 'echarts/charts';
import {
  DataZoomComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent
} from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';
import { provide, } from 'vue';

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
]);

provide(THEME_KEY, 'dark');

const props = defineProps({
  type: String,
  xdata: Array,
  ydata: Array,
});

const option = computed(() => {
  switch (props.type) {
    case 'bar':
    case 'line':
    case 'scatter':
      return {
        title: {
          show: false,
        },
        grid: {
          left: '80px',
          top: '20px',
          right: '80px',
          bottom: '60px'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
        },
        dataZoom: [
          {
            type: 'slider',
            start: 0,
            end: 1000
          }
        ],
        xAxis: {
          type: 'category',
          boundaryGap: props.type === 'bar',
          data: props.xdata,
          axisLabel: {
            fontSize: 10
          },
          axisTick: {
            alignWithLabel: true
          }
        },
        yAxis: {
          type: 'value',
        },
        series: [
          {
            data: props.ydata,
            type: props.type,
            itemStyle: {
              borderRadius: [10, 10, 0, 0],
            }
          }
        ]
      };
    case 'pie':
      return {
        title: {
          show: false,
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)',
        },
        series: [
          {
            name: '',
            type: 'pie',
            radius: '55%',
            center: ['50%', '50%'],
            data: merageData(),
            avoidLabelOverlap: true,
            itemStyle: {
              borderRadius: 5,
              borderColor: '#fff',
              borderWidth: 'auto'
            }
          },
        ],
      };
  }
});
const merageData = ()  => {
  if (props.xdata.length !== props.ydata.length) {
    console.log('xdata.length !== ydata.length');
    return [];
  }
  if (props.xdata.length === 0 || props.ydata.length === 0) {
    return [];
  }
  return props.xdata.map((name, index) => {
    return {
      name,
      value: props.ydata[index]
    };
  })
}

</script>

<style scoped>
.chart {
  height: 100vh;
}
</style>
