'''
Author:- vinay raju
Contributors:- -
Modified on:- 20/04/2023
Last mofified by:- vinay raju
Description of modification:- adding docs string and setting .env
'''



import os
from fastapi import FastAPI,Depends,Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, UploadFile, File,Form
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import json
from constants import *
from bson import json_util
from db_operation.mongo_crud import mongo_query
from logging_module.application_logging import logger
from authentication_module.authentication import *
from db_operation.mongo_crud import users
from handler.predict import  answer, chatpdf
import uuid

app = FastAPI()

# Set up CORS middleware to allow requests from any origin
origins = ["*"]

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:4200",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Login API
@app.get("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        logger.info("entered inside login endpoint")
        user = get_user(form_data.username)
        if not user:
            return {"message": "Incorrect email or password", "status": "failed"}
        if not verify_password(form_data.password, user.password):
            return {"message": "Incorrect email or password", "status": "failed"}
        
        access_token = create_access_token(data={"sub": user.email})
        user = users.find_one({"email": user.email})
        del user["_id"]
        del user["password"]
        return {"message": "login successful","status":"success","data":json.loads(json_util.dumps(user)),"access_token":access_token}
    
    except Exception as ex:
        logger.info("exception in login endpoint",ex)
        return {"message": "Exception occurred in login","status":"failed"}
    

# Signup API
@app.post("/signup")
async def signup(email:str=Body(...), password:str=Body(...), confirm_password:str=Body(...)):
    try:
        logger.info("entered inside training_access endpoint")
        if password==confirm_password:
            existing_user = get_user(email)
            if existing_user:
                return {"message": "Email already registered", "status": "failed"}
            create_user(email,password)
            return {"message": "successfully registered", "status": "success"}
        else:
            return {"message":"password not matching check the confirm password","status":"failed"}
        
    except Exception as ex:
        logger.info("exception in signup endpoint",ex)
        return {"message": "Exception occured in signup","status":"failed"}
    

@app.get("/start_session")
def new_session():
    '''start the session and create the uuid, set session time out for that specific session
    and create necessary key value pair in db'''

    try:
        logger.info("entered inside start_session endpoint")
        now = datetime.now()

        session_time_out = now + timedelta(hours=2)
        random_uuid = uuid.uuid4()
        hex_uuid = random_uuid.hex
        document=mongo_query.new_session(hex_uuid,session_time_out)
        return {"message":"new session created","status":"success","data":document}
    
    except Exception as ex:
        logger.info({"message":"exception in start_session end point","status":"failed","reason":ex})
        return {"message":"exception in start_session end point","status":"failed"}


@app.post("/file_upload")
async def file_upload(uuid:str= Form(),upload_file: UploadFile = File()):
    '''Upload the txt, pdf, docs files and extract the text,
    append the .txt file untill new session and update the db'''

    try:
        logger.info("entered inside file_upload endpoint")

        now = datetime.now()
        document=mongo_query.find_docs(uuid)
        expire_time=document["session_time_out"]
        file_type=upload_file.filename.split(".")[-1]

        if now<expire_time:
            logger.info("entered inside valid time session")
            time_stamp=datetime.utcnow()

            for key,extraction_type in list_file_types.items():
                if file_type.lower()==key:
                    logger.info("entered inside valid doc format")
                    file_path=f"{time_stamp}.{key}"

                    if not os.path.exists(f"{pwd}/file_upload"):
                        os.mkdir(f"{pwd}/file_upload")

                    if not os.path.exists(f"{pwd}/file_upload/txt_{uuid}"):
                        os.mkdir(f"{pwd}/file_upload/txt_{uuid}")

                    full_file_path = os.path.join(f"{pwd}/file_upload", file_path)
                    with open(full_file_path, 'wb') as f:
                        f.write(await upload_file.read())

                    txt_dir=f"{pwd}/file_upload/txt_{uuid}"
                    txt_path=f"{uuid}.txt"
                    txt_file_path=os.path.join(txt_dir, txt_path)
                    extracted_text=extraction_type(full_file_path,txt_file_path)

                    response = chatpdf(txt_file_path) # invoke chatgpt function

                    document=mongo_query.file_path_update(uuid,full_file_path,txt_file_path)
                    document=mongo_query.find_docs(uuid)

                    return {"message":"file uploaded successfully",
                            "status":"success", "data":document, "answer": response.get("answer"), "questions": response.get("questions") }
            return {"message":"invalid file format","status":"failed"}
        return {"message":"session expired refresh the session and try again","status":"failed"}
        
    except Exception as ex:
        logger.info({"message":"exception in file_upload end point","status":"failed","reason":ex})
        return {"message":"exception in file_upload end point","status":"failed"}
    

@app.post("/ask_query")
def chat_bot(uuid:str=Body(...),question:str=Body(...)):
    '''check if file path exsist in db and accept the question and calling the answer function to get the solution'''
    
    try:
        logger.info("entered inside chat_bot endpoint")

        document=mongo_query.find_docs(uuid)
        if not document["txt_file_path"]=="NA":
            logger.info("txt directory found")

            # solution = answer(document["txt_file_path"], document["uuid"], question)
            solution = chatpdf(document["txt_file_path"], question)

            if solution.get("status") =="failed":
                return JSONResponse(status_code=500, content={"status":"failed","message":"exception in model prediction"})
            
            mongo_query.question_answer_update(uuid, question, solution.get("answer") )

            return {"message":"successfully generated the answer","status":"success","data": solution.get("answer") }
        else:
            return {"message":"please upload the document","status":"failed"}

    except Exception as ex:
        logger.info({"message":"exception in chat_bot end point","status":"failed","reason":ex})
        return {"message":"exception in chat_bot end point","status":"failed"}


