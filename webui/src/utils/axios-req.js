import axios from 'axios'
import { ElLoading, ElMessage, ElMessageBox } from 'element-plus'
import { useBasicStore } from '@/store/basic'

//使用axios.create()创建一个axios请求实例
const service = axios.create()
let loadingInstance = null //loading实例
let tempReqUrlSave = ''
let authorTipDoor = true

const noAuthDill = () => {
  authorTipDoor = false
  ElMessageBox.confirm('请重新登录', {
    confirmButtonText: '重新登录',
    closeOnClickModal: false,
    showCancelButton: false,
    showClose: false,
    type: 'warning'
  }).then(() => {
    useBasicStore().resetStateAndToLogin()
    authorTipDoor = true
  })
}

//请求前拦截
service.interceptors.request.use(
  (req) => {
    const { token, axiosPromiseArr } = useBasicStore()
    //axiosPromiseArr收集请求地址,用于取消请求
    req.cancelToken = new axios.CancelToken((cancel) => {
      tempReqUrlSave = req.url
      axiosPromiseArr.push({
        url: req.url,
        cancel
      })
    })

    //设置token到header
    if (token) req.headers['Authorization'] = token
    //如果req.method给get 请求参数设置为 ?name=xxx
    if ('get'.includes(req.method?.toLowerCase()) && !req.params) req.params = req.data

    //req loading
    // @ts-ignore
    if (req.reqLoading ?? true) {
      loadingInstance = ElLoading.service({
        lock: true,
        fullscreen: true,
        // spinner: 'CircleCheck',
        text: '请稍后...',
        background: 'rgba(0, 0, 0, 0.1)'
      })
    }
    return req
  },
  (err) => {
    //发送请求失败
    Promise.reject(err)
  }
)
//请求后拦截
service.interceptors.response.use(
  (res) => {

    //取消请求
    useBasicStore().remotePromiseArrByReqUrl(tempReqUrlSave)
    if (loadingInstance) {
      loadingInstance && loadingInstance.close()
    }
    //download file
    if (res.data?.type?.includes("sheet")) {
      return res
    }

    if (res.config.type === 'chat') {
      return res
    }

    const { code, msg } = res.data
    const successCode = [0,200,20000]
    const noAuthCode = [401,403]
    if (successCode.includes(code)) {
      return res.data
    } else {
      //authorTipDoor 防止多个请求 多次alter
      if (authorTipDoor) {
        if (noAuthCode.includes(code)) {
          noAuthDill()
        } else {
          // @ts-ignore
          if (!res.config?.isNotTipErrorMsg) {
            ElMessage.error({
              message: msg,
              duration: 2 * 1000
            })
          } else {
            return res
          }
          return Promise.reject(msg)
        }
      }
    }
  },
  //响应报错
  (err) => {
    //取消请求
    useBasicStore().remotePromiseArrByReqUrl(tempReqUrlSave)
    if (loadingInstance) {
      loadingInstance && loadingInstance.close()
    }
    ElMessage.error({
      message: err,
      duration: 2 * 1000
    })
    return Promise.reject(err)
  }
)
//导出service实例给页面调用 , config->页面的配置
export default function axiosReq(config) {
  return service({
    baseURL: import.meta.env.VITE_APP_BASE_URL,
    timeout: 8000,
    ...config
  })
}
