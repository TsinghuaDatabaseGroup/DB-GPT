import { post } from '@/api/request'

export async function run(args) {
  return await post('db_diag/run', args)
}

export async function nextStep(args) {
  return await post('db_diag/next_step', args)
}
