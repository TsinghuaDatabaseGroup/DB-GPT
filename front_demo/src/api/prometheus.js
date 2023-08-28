import axios from 'axios'
import { Message } from 'element-ui'

// create an axios instance
const service = axios.create({
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

export function get(baseUrl, url, params) {
  return service({
    baseURL: baseUrl,
    url: url,
    method: 'get',
    params: params
  })
}

export async function query(baseUrl, params) {
  return await get(baseUrl, 'api/v1/query', params)
}

export async function query_range(baseUrl, params) {
  return await get(baseUrl, 'api/v1/query_range', params)
}

export async function series(baseUrl, params) {
  return await get(baseUrl, 'api/v1/series', params)
}
