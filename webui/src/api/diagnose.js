import axiosReq from '@/utils/axios-req'

// 获取诊断状态
export const diagnoseStatusReq = () => {
  return axiosReq({
    url: 'diagnose/diagnose_status',
    method: 'get',
    reqLoading: false
  })
}


//上传文件并诊断
export const runDiagnoseReq = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return axiosReq({
    url: 'diagnose/run_diagnose',
    data: formData,
    method: 'post',
    cache: false,
    contentType: false,
    processData: false,
    timeout: 0,
  })
}


// 获取诊断的终端输出
export const diagnoseTerminalOutputReq = () => {
  return axiosReq({
    url: 'diagnose/terminal_output',
    method: 'get',
    reqLoading: false
  })
}

// 获取诊断的格式化输出
export const diagnoseSerializationOutputReq = () => {
  return axiosReq({
    url: 'diagnose/serialization_output',
    method: 'get',
    reqLoading: false
  })
}

// 停止诊断任务
export const diagnoseStopDiagnoseReq = () => {
  return axiosReq({
    url: 'diagnose/stop_diagnose',
    data: {},
    method: 'post',
    reqLoading: true
  })
}

// 诊断时用户反馈
export const diagnoseUserFeedbackReq = (input) => {
  return axiosReq({
    url: 'diagnose/user_feedback',
    data: {user_input: input},
    method: 'post',
    reqLoading: false
  })
}
