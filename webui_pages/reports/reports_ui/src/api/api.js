import { post } from '@/api/request'

export async function alertHistories(args) {
  return await post('alert/report/histories', args)
}

export async function alertHistoryDetail(args) {
  return await post('alert/report/history_detail', args)
}

export async function diagnose_llm_model_list() {
  return await post('alert/report/diagnose_llm_model_list', {})
}
