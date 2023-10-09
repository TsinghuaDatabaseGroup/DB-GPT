export const pickerOptions = {
  shortcuts: [
    {
      text: '最近5分钟',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 60 * 5 * 1000)
        picker.$emit('pick', [start, end])
      }
    },
    {
      text: '最近15分钟',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 60 * 15 * 1000)
        picker.$emit('pick', [start, end])
      }
    },
    {
      text: '最近30分钟',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 60 * 30 * 1000)
        picker.$emit('pick', [start, end])
      }
    },
    {
      text: '最近1小时',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 1000)
        picker.$emit('pick', [start, end])
      }
    },
    {
      text: '最近6小时',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 6 * 1000)
        picker.$emit('pick', [start, end])
      }
    },
    {
      text: '最近12小时',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 12 * 1000)
        picker.$emit('pick', [start, end])
      }
    },
    {
      text: '最近24小时',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 24 * 1000)
        picker.$emit('pick', [start, end])
      }
    },
    {
      text: '最近7天',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
        picker.$emit('pick', [start, end])
      }
    }, {
      text: '最近30天',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
        picker.$emit('pick', [start, end])
      }
    }, {
      text: '最近90天',
      onClick(picker) {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
        picker.$emit('pick', [start, end])
      }
    }
  ]
}
