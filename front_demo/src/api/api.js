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

export async function nextStep(args) {
  return await post('db_diag/next_step', args)
}
