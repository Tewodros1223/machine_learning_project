import React from 'react'
import Register from './components/Register'
import Login from './components/Login'
import Quiz from './components/Quiz'

export default function App(){
  return (
    <div style={{padding:20}}>
      <h2>Face Quiz Demo</h2>
      <Register />
      <hr />
      <Login />
      <hr />
      <Quiz token={localStorage.getItem('access_token') || ''} />
    </div>
  )
}
