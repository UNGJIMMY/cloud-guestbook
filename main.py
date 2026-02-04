from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1. 앱 설정
app = FastAPI()

# 2. 데이터베이스 설정 (나중에 환경변수로 받을 것임)
# 기본값은 로컬 테스트용이고, 배포 시 환경변수가 덮어씌웁니다.
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "gdb00000")
DB_HOST = os.getenv("DB_HOST", "localhost") # 나중에 AWS RDS 주소 넣을 곳
DB_PORT = "3306"
DB_NAME = "guestbook"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# DB 연결 엔진 생성 (접속 실패시 에러가 날 텐데, 일단 코드는 작성해둠)
# 실제 연결은 DB가 생성되고 주소를 받아와야 가능함.
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except:
    print("DB 연결 정보가 아직 없거나 틀립니다. (정상)")
    engine = None
    Base = object # 임시

# 3. 테이블 모델 정의 (테이블명: messages)
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(200))

# 4. DB 테이블 자동 생성 (테이블 없으면 만듦)
if engine:
    try:
        Base.metadata.create_all(bind=engine)
    except:
        pass

# 5. 데이터 받을 형식 정의 (DTO)
class MessageCreate(BaseModel):
    content: str

# 6. API 만들기
@app.get("/")
def read_root():
    return {"Hello": "Junior DBA", "Project": "Guestbook"}

@app.post("/write")
def create_message(msg: MessageCreate):
    if not engine:
        return {"error": "DB not connected"}
    
    session = SessionLocal()
    new_msg = Message(content=msg.content)
    session.add(new_msg)
    session.commit()
    session.close()
    return {"status": "Message Saved!", "content": msg.content}

@app.get("/list")
def read_messages():
    if not engine:
        return {"error": "DB not connected"}

    session = SessionLocal()
    msgs = session.query(Message).all()
    session.close()
    return msgs