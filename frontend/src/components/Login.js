import React, {useRef, useState} from 'react'
import FaceCapture from './FaceCapture'

export default function Login(){
  const emailRef = useRef()
  const passRef = useRef()
  const [token, setToken] = useState(() => localStorage.getItem('access_token') || '')

  const login = async () =>{
    const res = await fetch('http://localhost:8000/login',{
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email: emailRef.current.value, password: passRef.current.value})
    })
    const data = await res.json()
    if(res.ok){
      setToken(data.access_token)
      localStorage.setItem('access_token', data.access_token)
    } else {
      alert(data.detail || 'Login failed')
    }
  }

  return (
    <div>
      <h3>Login</h3>
      <input placeholder="email" ref={emailRef} /> <br/>
      <input placeholder="password" type="password" ref={passRef} /> <br/>
      <button onClick={login}>Login</button>
      <div>Token: {token ? 'Received' : 'Not logged in'}</div>
      {token && <div style={{marginTop:8}}><FaceCapture token={token} /></div>}
    </div>
  )
}
