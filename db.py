import pymongo
import dotenv
import os
dotenv.load_dotenv(override=True)

def get_collection():
    try:
        mongo = pymongo.MongoClient(os.getenv("DATABASE_URL"))
        db = mongo['MMTESTDB']
        return db['callwarningcount']
    except Exception as e:
        print(e)    

