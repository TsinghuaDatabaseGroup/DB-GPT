import axios from 'axios'
import { Message } from 'element-ui'

// create an axios instance
const service = axios.create({
  baseURL: 'http://8.131.229.55:9090', // url = base url + request url
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
    if (res.status !== 'success') {
      Message({
        message: res.massage || 'Please try again later',
        type: 'error'
      })
      return Promise.reject(new Error(res.message || 'Error'))
    } else {
      return res
    }
  },
  error => {
    Message({
      message: error.msg,
      type: 'error'
    })
    return Promise.reject(error)
  }
)

export function get(url, params) {
  return service({
    url: url,
    method: 'get',
    params: params
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

export async function query(params) {
  return await get('api/v1/query', params)
}

export async function query_range(params) {
  return await get('api/v1/query_range', params)
}

export async function series(params) {
  return await get('api/v1/series', params)
}

export async function label_datname_values(params) {
  return await get('label/datname/values', params)
}
