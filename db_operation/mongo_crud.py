from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

ROOT_PATH = os.path.abspath('')
ENV = os.path.join(ROOT_PATH, '.env')
load_dotenv(ENV)

MONGO_DB = os.getenv('MONGODB')
MONGO_HOST = os.getenv('MONGO_HOST')  # mongo
MONGO_PORT = os.getenv('MONGODB_PORT')  # mongo
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', '')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')

connecting_str=f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
client = MongoClient(connecting_str)

db = client["explore_docs"]
users = db["users"]
virtual_chats=db["explore_docs_chats"]


class mongo_query:
    
    def new_session(hex_uuid,session_time_out):
        try:
            document={
                "session_time_out":session_time_out,
                "uuid":hex_uuid,
                "txt_file_path":"NA",
                "chats":[],
                "uploaded_files":[],
                "created_at":datetime.utcnow()
            }
            virtual_chats.insert_one(document)
            del document["_id"]
            return document
        
        except Exception as ex:
            print({"message":"exception in new_session","status":"failed","reason":ex})
            return {"message":"exception in new_session","status":"failed"}


    def find_docs(uuid):
        try:
            document=virtual_chats.find_one({"uuid":uuid})
            del document["_id"]
            return document
        
        except Exception as ex:
            print({"message":"exception in find_docs","status":"failed","reason":ex})
            return {"message":"exception in find_docs","status":"failed"}
        

    def file_path_update(uuid,full_file_path,txt_file_path):
        try:

            document=virtual_chats.update_one({"uuid":uuid},{"$set":{"txt_file_path":txt_file_path},
                                              "$push": {"uploaded_files": full_file_path}})
            return document
        
        except Exception as ex:
            print({"message":"exception in file_path_update","status":"failed","reason":ex})
            return {"message":"exception in file_path_update","status":"failed"}


    def question_answer_update(uuid,question,solution):
        try:
            new_chat={"question":question,"answer":solution}
            virtual_chats.update_one(
                {"uuid": uuid},
                {"$push": {"chats": new_chat}}
            )
        
        except Exception as ex:
            print({"message":"exception in question_answer_update","status":"failed","reason":ex})
            return {"message":"exception in question_answer_update","status":"failed"}
