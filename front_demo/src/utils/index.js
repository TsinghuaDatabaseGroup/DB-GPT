/**
 * Created by PanJiaChen on 16/11/18.
 */

/**
 * Parse the time to string
 * @param {(Object|string|number)} time
 * @param {string} cFormat
 * @returns {string | null}
 */
export function parseTime(time, cFormat) {
  if (arguments.length === 0 || !time) {
    return null
  }
  const format = cFormat || '{y}-{m}-{d} {h}:{i}:{s}'
  let date
  if (typeof time === 'object') {
    date = time
  } else {
    if ((typeof time === 'string')) {
      if ((/^[0-9]+$/.test(time))) {
        // support "1548221490638"
        time = parseInt(time)
      } else {
        // support safari
        // https://stackoverflow.com/questions/4310953/invalid-date-in-safari
        time = time.replace(new RegExp(/-/gm), '/')
      }
    }

    if ((typeof time === 'number') && (time.toString().length === 10)) {
      time = time * 1000
    }
    date = new Date(time)
  }
  const formatObj = {
    y: date.getFullYear(),
    m: date.getMonth() + 1,
    d: date.getDate(),
    h: date.getHours(),
    i: date.getMinutes(),
    s: date.getSeconds(),
    a: date.getDay()
  }
  const time_str = format.replace(/{([ymdhisa])+}/g, (result, key) => {
    const value = formatObj[key]
    // Note: getDay() returns 0 on Sunday
    if (key === 'a') { return ['日', '一', '二', '三', '四', '五', '六'][value ] }
    return value.toString().padStart(2, '0')
  })
  return time_str
}

/**
 * @param {number} time
 * @param {string} option
 * @returns {string}
 */
export function formatTime(time, option) {
  if (('' + time).length === 10) {
    time = parseInt(time) * 1000
  } else {
    time = +time
  }
  const d = new Date(time)
  const now = Date.now()

  const diff = (now - d) / 1000

  if (diff < 30) {
    return '刚刚'
  } else if (diff < 3600) {
    // less 1 hour
    return Math.ceil(diff / 60) + '分钟前'
  } else if (diff < 3600 * 24) {
    return Math.ceil(diff / 3600) + '小时前'
  } else if (diff < 3600 * 24 * 2) {
    return '1天前'
  }
  if (option) {
    return parseTime(time, option)
  } else {
    return (
      d.getMonth() +
      1 +
      '月' +
      d.getDate() +
      '日' +
      d.getHours() +
      '时' +
      d.getMinutes() +
      '分'
    )
  }
}

/**
 * @param {string} url
 * @returns {Object}
 */
export function param2Obj(url) {
  const search = decodeURIComponent(url.split('?')[1]).replace(/\+/g, ' ')
  if (!search) {
    return {}
  }
  const obj = {}
  const searchArr = search.split('&')
  searchArr.forEach(v => {
    const index = v.indexOf('=')
    if (index !== -1) {
      const name = v.substring(0, index)
      const val = v.substring(index + 1, v.length)
      obj[name] = val
    }
  })
  return obj
}

// 秒转时间
export function formatSeconds(value) {
  var theTime = parseInt(value)// 需要转换的时间秒
  var theTime1 = 0// 分
  var theTime2 = 0// 小时
  var theTime3 = 0// 天

  if (theTime > 60) {
    theTime1 = parseInt(theTime / 60)
    theTime = parseInt(theTime % 60)
    if (theTime1 > 60) {
      theTime2 = parseInt(theTime1 / 60)
      theTime1 = parseInt(theTime1 % 60)
      if (theTime2 > 24) {
        // 大于24小时
        theTime3 = parseInt(theTime2 / 24)
        theTime2 = parseInt(theTime2 % 24)
      }
    }
  }
  var result = ''
  if (theTime > 0 && theTime2 === 0 && theTime3 === 0) {
    result = ' ' + parseInt(theTime) + 's'
  }
  if (theTime1 > 0 && theTime3 === 0) {
    result = ' ' + parseInt(theTime1) + 'm' + result
  }
  if (theTime2 > 0) {
    result = ' ' + parseInt(theTime2) + 'h' + result
  }
  if (theTime3 > 0) {
    result = ' ' + parseInt(theTime3) + 'd' + result
  }
  return result
}

// 字节转大小
export function bytesToSize(bytes) {
  if (parseInt(bytes) === 0) {
    return '0 B'
  }

  var k = 1024

  const sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  var num = bytes / Math.pow(k, i)
  return parseFloat(num.toPrecision(3)) + ' ' + sizes[i]
}

export function bytesToSizeSecondsRate(bytes) {
  if (parseInt(bytes) === 0) {
    return '0 B/s'
  }

  var k = 1024

  const minus = bytes < 0

  if (minus) {
    bytes = bytes * -1
  }

  const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s', 'PB/s', 'EB/s', 'ZB/s', 'YB/s']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  var num = bytes / Math.pow(k, i)
  return (minus ? '-' : '') + parseFloat(num.toPrecision(3)) + ' ' + sizes[i]
}

// 转百分数
export function stringToPercent(point) {
  point = parseFloat(point)
  if (point === 0) {
    return '0 %'
  }
  var str = parseFloat(Number(point).toFixed(2))
  str += '%'
  return str
}

export function stringFoFixed2(point) {
  point = parseFloat(point)
  if (point === 0) {
    return '0'
  }
  var str = parseFloat(Number(point).toFixed(2))
  return str
}

export function numConvert(value) {
  value = parseFloat(value)
  if (value >= 10000) {
    value = parseFloat(Math.round(value / 1000) / 10) + 'w'
  } else if (value >= 1000) {
    value = parseFloat(Math.round(value / 100) / 10) + 'k'
  } else {
    value = parseFloat(Number(value).toFixed(2))
  }
  return value
}

export function format_plan_data(item, data) {
  if (!item) {
    return data
  }

  const plans = item['Plans']
  const name = item['Node Type'] + '\n' + 'cost：' + item['Startup Cost']

  if (plans) {
    if (plans.length === 1) {
      const format_data_result = format_plan_data(plans[0], [])
      data = {
        'name': name,
        'children': [format_data_result]
      }
    } else {
      var children = []
      for (let i = 0; i < plans.length; i++) {
        const format_data_result = format_plan_data(plans[i], {})
        children.push(format_data_result)
        data = {
          'name': name,
          'children': children
        }
      }
    }
  } else {
    data = {
      'name': name,
      'value': ''
    }
  }
  return data
}
