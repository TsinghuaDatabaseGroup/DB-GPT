// LLm模型聊天
import axiosReq from "@/utils/axios-req";

export const alertHistories = (start, end, model) => {
  return axiosReq({
    url: 'report/histories',
    data: {start, end, model},
    method: 'post'
  })
}

export const alertHistoryDetail = (file, model) => {
  return axiosReq({
    url: 'report/history_detail',
    data: {file, model},
    method: 'post'
  })
}

export const diagnoseLlmModelList = () => {
  return axiosReq({
    url: 'report/diagnose_llm_model_list',
    data: {},
    method: 'post'
  })
}
