import { post } from '@/api/request'

export async function uploadFile(params) {
  var form = new FormData()
  for (var key in params) {
    form.append(key, params[key])
  }
  return await post('admin/upload_file', form, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export async function sqlCheck(args) {
  return await post('sql_check', args)
}

