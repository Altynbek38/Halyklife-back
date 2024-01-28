from datetime import datetime
from pymongo.database import Database
from fastapi import HTTPException

class History:
    def __init__(self, database: Database):
        self.database = database
    
    def check_by_iin(self, user_iin):
        civilian_iin = self.database["civilian_db"].find_one({"iin": user_iin})
        if not civilian_iin:
            return HTTPException(status_code=404, detail="Not Found")

        return HTTPException(status_code=200, detail="OK")
    

    def check_certificate(self, user_iin, guid):
        civilian = self.database["civilian_db"].find_one({"iin": user_iin})
        
        if civilian is not None and guid in civilian.get("certificate", {}).get("GUID", []):
            return HTTPException(status_code=200, detail="OK")
        
        return HTTPException(status_code=404, detail="Not Found")


           