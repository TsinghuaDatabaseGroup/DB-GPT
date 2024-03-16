import {ref} from 'vue';

export function fetchData(url, data = {}) {
  const isDone = ref(false);
  const fetchResult = ref([]);

  fetch(import.meta.env.VITE_APP_BASE_URL + url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(response => {
      const reader = response.body.getReader();
      return new ReadableStream({
        start(controller) {
          function push() {
            reader.read().then(({done, value}) => {
              if (done) {
                controller.close();
                isDone.value = true;
                return;
              }
              const decoder = new TextDecoder('utf-8');
              const resonseStr = decoder.decode(value);
              // console.log(resonseStr);
              try {
                const jsonObj = JSON.parse(resonseStr);
                fetchResult.value.push(jsonObj);
              } catch {
                const jsonArray = resonseStr.match(/{.*?}(?=({|$))/g);
                // 解析每个 JSON 字符串，将结果添加到 fetchResult 中
                jsonArray.forEach(jsonStr => {
                  try {
                    const jsonObj = JSON.parse(jsonStr);
                    fetchResult.value.push(jsonObj);
                  } catch (e) {
                    console.error(e);
                  }
                });
              }
              controller.enqueue(value);
              push();
            });
          }

          push();
        }
      });
    })

  return {isDone, fetchResult};
}
