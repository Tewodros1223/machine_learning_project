import React, {useState} from 'react'
import FaceCapture from './FaceCapture'

export default function Quiz({token}){
  const [state, setState] = useState({stage: 'idle', quiz: null, message: ''})

  const start = async ()=>{
    setState(s=>({...s, message:'Starting...'}))
    const res = await fetch('http://localhost:8000/quiz/start',{
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    if(!res.ok){
      setState({stage:'error', message: JSON.stringify(data)})
      return
    }
    if(data.require_face_reauth){
      setState({stage:'reauth', quiz: data})
    } else {
      setState({stage:'quiz', quiz: data})
    }
  }

  const onVerify = (result)=>{
    if(result.match){
      setState(s=>({...s, stage:'quiz', message:'Face verified'}))
    } else {
      setState(s=>({...s, message:'Face not matched'}))
    }
  }

  const submit = async ()=>{
    if(!state.quiz) return
    // read answers from form
    const answers = {}
    state.quiz.data.questions.forEach(q=>{
      const el = document.querySelector(`[name='q_${q.id}']`)
      if(el) answers[q.id] = el.value
    })
    const res = await fetch('http://localhost:8000/quiz/submit',{
      method: 'POST',
      headers: {'Content-Type':'application/json', 'Authorization': `Bearer ${token}`},
      body: JSON.stringify({quiz_id: state.quiz.quiz_id, answers: {answers}})
    })
    const data = await res.json()
    if(res.ok) setState({stage:'done', message:`Score: ${data.score}`})
    else setState({stage:'error', message: JSON.stringify(data)})
  }

  return (
    <div style={{marginTop:20}}>
      <h3>Quiz</h3>
      {state.stage === 'idle' && <button onClick={start}>Start Quiz</button>}
      {state.stage === 'reauth' && (
        <div>
          <div>Face re-authentication required before starting the quiz.</div>
          <FaceCapture token={token} path={'/face/verify'} onResult={onVerify} buttonLabel={'Verify & Start'} />
          <div>{state.message}</div>
        </div>
      )}
      {state.stage === 'quiz' && state.quiz && (
        <div>
          <h4>{state.quiz.title}</h4>
          {state.quiz.data.questions.map(q=> (
            <div key={q.id} style={{marginBottom:8}}>
              <div>{q.q}</div>
              <select name={`q_${q.id}`}>
                {q.choices.map(c=> <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          ))}
          <button onClick={submit}>Submit</button>
          <div>{state.message}</div>
        </div>
      )}
      {state.stage === 'done' && <div>{state.message}</div>}
      {state.stage === 'error' && <div style={{color:'red'}}>{state.message}</div>}
    </div>
  )
}
