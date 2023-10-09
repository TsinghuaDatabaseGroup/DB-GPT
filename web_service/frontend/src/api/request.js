import axios from 'axios'
import { Message } from 'element-ui'
import qs from 'qs'

// create an axios instance
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
  timeout: 12000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 0) {
      Message({
        message: res.msg || 'Error',
        type: 'error',
        duration: 5 * 1000
      })
      return Promise.reject(new Error(res.message || 'Error'))
    } else {
      return res
    }
  },
  error => {
    Message({
      message: error.msg,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)
export function uploadFile(url, params) {
  var form = new FormData()
  for (var key in params) {
    form.append(key, params[key])
  }
  return post(url, form, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function get(url, params) {
  return service({
    url: url,
    method: 'get',
    params: qs.stringify(params, { indices: false })
  })
}

export function put(url, data) {
  return service({
    url: url,
    method: 'put',
    data: qs.stringify(data, { indices: false })
  })
}

export function patch(url, data) {
  return service({
    url: url,
    method: 'patch',
    data: qs.stringify(data, { indices: false })
  })
}

export function post(url, data, config = {}) {
  return service({
    url: url,
    method: 'post',
    data: data,
    timeout: config.timeout,
    config: config
  })
}

export default service
