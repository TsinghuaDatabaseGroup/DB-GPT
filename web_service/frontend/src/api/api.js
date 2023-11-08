import { post } from '@/api/request'

export async function robotIntro(args) {
  return await post('db_diag/robot_intro', args)
}

export async function instances(args) {
  return await post('config/instances', args)
}

export async function run(args) {
  return await post('db_diag/run', args)
}

export async function history(args) {
  return await post('db_diag/chat_history', args)
}

export async function nextStep(args) {
  return await post('db_diag/next_step', args)
}

export async function alertHistories(args) {
  return await post('histories', args)
}

export async function alertHistoryDetail(args) {
  return await post('history-detail', args)
}
