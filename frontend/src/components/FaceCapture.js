import React, {useRef, useEffect, useState} from 'react'

export default function FaceCapture({token, path = '/face/verify', onResult = null, buttonLabel = 'Verify Face'}){
  const videoRef = useRef()
  const canvasRef = useRef()
  const [msg, setMsg] = useState('')

  useEffect(()=>{
    async function start(){
      try{
        const stream = await navigator.mediaDevices.getUserMedia({video:true})
        videoRef.current.srcObject = stream
        videoRef.current.play()
      } catch(e){
        setMsg('Camera error: ' + e.message)
      }
    }
    start()
    return ()=>{
      if(videoRef.current && videoRef.current.srcObject){
        const tracks = videoRef.current.srcObject.getTracks()
        tracks.forEach(t => t.stop())
      }
    }
  },[])

  const captureBlob = () => new Promise(resolve => {
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    canvas.toBlob(blob => resolve(blob), 'image/jpeg')
  })

  const upload = async (pathToUse) =>{
    setMsg('Processing...')
    const blob = await captureBlob()
    const fd = new FormData()
    fd.append('file', blob, 'capture.jpg')
    try{
      const res = await fetch(`http://localhost:8000${pathToUse}`,{
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: fd
      })
      const data = await res.json()
      if(!res.ok){
        setMsg(data.detail || JSON.stringify(data))
      } else {
        setMsg(JSON.stringify(data))
        if(onResult) onResult(data)
      }
    } catch(e){
      setMsg('Upload error: ' + e.message)
    }
  }

  return (
    <div>
      <h4>Face Capture</h4>
      <video ref={videoRef} style={{width:320,height:240,border:'1px solid #ccc'}} />
      <canvas ref={canvasRef} style={{display:'none'}} />
      <div style={{marginTop:8}}>
        <button onClick={()=>upload('/face/register')}>Register Face</button>
        <button onClick={()=>upload(path)}>{buttonLabel}</button>
      </div>
      <div style={{marginTop:8}}>{msg}</div>
    </div>
  )
}
