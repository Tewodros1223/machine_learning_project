import React, {useRef, useState} from 'react'

export default function Register(){
  const emailRef = useRef()
  const passRef = useRef()
  const [msg, setMsg] = useState('')

  const register = async () =>{
    const res = await fetch('http://localhost:8000/register',{
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email: emailRef.current.value, password: passRef.current.value})
    })
    if(res.ok){
      setMsg('Registered successfully')
    } else {
      const d = await res.json()
      setMsg(d.detail || 'Error')
    }
  }

  return (
    <div>
      <h3>Register</h3>
      <input placeholder="email" ref={emailRef} /> <br/>
      <input placeholder="password" type="password" ref={passRef} /> <br/>
      <button onClick={register}>Register</button>
      <div>{msg}</div>
    </div>
  )
}
