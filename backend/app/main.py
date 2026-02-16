import os
import base64
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models, schemas, auth, face_service
from .middleware import RateLimitMiddleware, MaxUploadSizeMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FaceAuth Quiz API")

# Security middlewares
app.add_middleware(RateLimitMiddleware)
app.add_middleware(MaxUploadSizeMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed, full_name=user_in.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = auth.create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/face/register")
def face_register(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    content = file.file.read()
    try:
        emb = face_service.face_service.get_embedding(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # store embedding as bytes
    emb_bytes = emb.tobytes()
    existing = db.query(models.FaceEmbedding).filter(models.FaceEmbedding.user_id == current_user.id).first()
    if existing:
        existing.embedding = emb_bytes
    else:
        fe = models.FaceEmbedding(user_id=current_user.id, embedding=emb_bytes)
        db.add(fe)
    db.commit()
    return {"status": "ok"}


@app.post("/face/verify")
def face_verify(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    content = file.file.read()
    try:
        emb = face_service.face_service.get_embedding(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    fe = db.query(models.FaceEmbedding).filter(models.FaceEmbedding.user_id == current_user.id).first()
    if not fe:
        raise HTTPException(status_code=404, detail="No face registered")
    stored = fe.embedding
    import numpy as np
    stored_emb = np.frombuffer(stored, dtype=np.float32)
    score = face_service.face_service.compare_embeddings(emb, stored_emb)
    threshold = float(os.getenv("FACE_MATCH_THRESHOLD", "0.5"))
    return {"score": score, "match": score >= threshold}


@app.post("/password-reset/request")
def password_reset_request(req: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        return {"status": "ok"}
    import secrets
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    pr = models.PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
    db.add(pr)
    db.commit()
    # In production, send email with token link. Here we return token for demo.
    return {"status": "ok", "token": token}


@app.post("/password-reset/confirm")
def password_reset_confirm(req: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    pr = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token == req.token).first()
    if not pr or pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == pr.user_id).first()
    user.hashed_password = auth.get_password_hash(req.new_password)
    db.delete(pr)
    db.commit()
    return {"status": "ok"}


@app.post("/quiz/start")
def quiz_start(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Check if user has a face registered
    fe = db.query(models.FaceEmbedding).filter(models.FaceEmbedding.user_id == current_user.id).first()
    require_face = bool(fe)
    # Return a simple sample quiz (in a real app this would come from DB)
    quiz = {
        "quiz_id": 1,
        "title": "Sample Quiz",
        "data": {"questions": [
            {"id": 1, "q": "What is 2+2?", "choices": ["3","4","5"]},
            {"id": 2, "q": "Select color of sky", "choices": ["Blue","Green","Red"]}
        ]}
    }
    return {"quiz_id": quiz["quiz_id"], "title": quiz["title"], "data": quiz["data"], "require_face_reauth": require_face}


@app.post("/quiz/submit", response_model=schemas.QuizSubmitOut)
def quiz_submit(payload: schemas.QuizSubmitIn, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Simple scoring: correct answers are hard-coded for demo
    correct = {1: "4", 2: "Blue"}
    answers = payload.answers.get("answers", {})
    score = 0
    for qid, ans in answers.items():
        try:
            qid_int = int(qid)
        except Exception:
            continue
        if correct.get(qid_int) == ans:
            score += 1
    # Persist response
    import json
    qr = models.QuizResponse(quiz_id=payload.quiz_id, user_id=current_user.id, answers=json.dumps(answers), score=score)
    db.add(qr)
    db.commit()
    return {"score": score}
