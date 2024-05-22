const videolist = document.createElement('div')

const text = document.createElement("pre")

document.querySelectorAll(".tr_window__recordings_list_cont button").forEach(button => {
  button.click()

  const title = document.querySelector('.tr_window__recordings_list_select_active_text').innerHTML
  const iframeUrl = document.querySelector('#iframe-translation').getAttribute('src')
  const videoId = iframeUrl.split('/')[5]
  const url = "https://vz-3c1714c0-443.b-cdn.net/" + videoId + "/1080p/"
  
  text.innerHTML += `${url} +  + ${title}\n`
  console.log(`${url} +  + ${title}`)
})

videolist.appendChild(text)
videolist.style = "position: fixed; background: white; height: 600px; top: 20px; left: 50%; transform: translate(-50%, 0); font-size: 10px; overflow-y: auto; padding: 20px; border: 2px solid black;"
document.querySelector('body').appendChild(videolist)