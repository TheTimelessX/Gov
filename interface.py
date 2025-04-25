from typing import Literal
import json

roles = Literal[
    'null',
    'member',
    'police',
    'manager',
    'leader'
]

roles_list = [
    'null',
    'member',
    'police',
    'manager',
    'leader'
]

class UserInterface(object):
    def __init__(self, result: tuple = ()):
        self.result = result
        if len(result) > 0:
            self.uid: int = self.result[0]
            self.role: roles = self.result[1]
            self.prom_by: int = self.result[2]
        
        else:
            self.uid: int = 0
            self.role: roles = "null"
            self.prom_by: int = 0

class AdminInterface(object):
    def __init__(self, result: tuple = ()):
        self.result = result
        if len(result) > 0:
            self.uid: int = self.result[0]
        else:
            self.uid: int = 0

class UserResponse(object):
    def __init__(self, resp: dict = {}):
        self.resp = resp
        self.status: str = self.resp.get("status", "ERROR")
        self.message: str = self.resp.get("message", "")
        self.user: UserInterface = UserInterface(self.resp.get("user", tuple()))

    def __str__(self):
        return json.dumps(self.resp, indent=2)
    
    def create_status(self):
        return {
            "status": self.status,
            "message": self.message
        }
    
class AdminResponse(object):
    def __init__(self, resp: dict = {}):
        self.resp = resp
        self.status: str = self.resp.get("status", "ERROR")
        self.message: str = self.resp.get("message", "")
        self.admin: AdminInterface = AdminInterface(self.resp.get("admin", tuple()))

    def __str__(self):
        return json.dumps(self.resp, indent=2)