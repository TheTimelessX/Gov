import sqlite3
import json
from interface import ( UserInterface, UserResponse, AdminInterface, AdminResponse, roles )

class UserManager(object):
    def __init__(self):
        self.dbs = sqlite3.connect("./users.db", check_same_thread=False)
        self.setup()

        self.options: dict[roles, list[str]] = {
            "police": [
                "member"
            ],
            "manager": [
                "member",
                "police",
                "manager"
            ],
            "leader": [
                "member",
                "police",
                "manager",
                "leader"
            ]
        }

    def setup(self):
        self.dbs.execute("CREATE TABLE IF NOT EXISTS gov_users (uid INTEGER PRIMARY KEY, role TEXT, prom_by TEXT)")
        self.dbs.execute("CREATE TABLE IF NOT EXISTS gov_admins (uid INTEGER PRIMARY KEY)")
        self.dbs.execute("CREATE TABLE IF NOT EXISTS options (role TEXT PRIMARY KEY, can_prom TEXT)")

    async def getAllOptions(self):
        return self.dbs.execute("SELECT * FROM options").fetchall()

    async def getOption(self, role: str):
        for option in await self.getAllOptions():
            if option[0] == "role":
                option[1] = json.loads(option[1])
                return {
                    "status": "OK",
                    "option": option
                }
            
        return {
            "status": "ERROR",
            "message": "Cannot find role"
        }
    
    async def resetOptions(self):
        alloptions = await self.getAllOptions()
        if len(alloptions) > 0:
            for opt in alloptions:
                self.dbs.execute("DELETE FROM options WHERE role = ?", (
                    opt[0],
                ))
        
        allkeys = list(self.options.keys())

        for key in allkeys:
            self.dbs.execute("INSERT INTO options (role, can_prom) VALUES (?, ?)", (
                key,
                self.options[key]
            ))
        
        self.dbs.commit()

        return {
            "status": "OK"
        }
    
    async def getAll(self) -> list[UserInterface]:
        return [UserInterface(u) for u in self.dbs.execute("SELECT * FROM gov_users").fetchall()]
    
    async def getAllAdmins(self) -> list[AdminInterface]:
        return [AdminInterface(u) for u in self.dbs.execute("SELECT * FROM gov_admins").fetchall()]
    
    async def getUserByUid(self, uid: int) -> UserResponse:
        for user in await self.getAll():
            if user.uid == uid:
                return UserResponse(
                    {
                        "status": "OK",
                        "user": user.result
                    }
                )
            
        return UserResponse(
            {
                "status": "ERROR",
                "message": "INVALID_USER_ID"
            }
        )
    
    async def getAdminByUid(self, uid: int) -> AdminResponse:
        for admin in await self.getAllAdmins():
            if admin.uid == uid:
                return AdminResponse(
                    {
                        "status": "OK",
                        "admin": admin.result
                    }
                )
            
        return AdminResponse(
            {
                "status": "ERROR",
                "message": "INVALID_USER_ID"
            }
        )
    
    async def add(self, uid: int) -> UserResponse:
        user = await self.getUserByUid(uid)

        if user.status == "OK":
            return UserResponse({
                "status": "ERROR",
                "message": "User exists"
            })
        
        self.dbs.execute(
            "INSERT INTO gov_users (uid, role, prom_by) VALUES (?, ?, ?)",
            (
                uid,
                "member",
                0
            )
        )
        self.dbs.commit()

        return UserResponse({
            "status": "OK",
            "user": (
                uid,
                "member",
                0
            )
        })
    
    async def calculate(self, from_action: roles, to_action: roles):
        if from_action == "leader":return 0
        if to_action == "leader": return 1
        if from_action == "manager": return 0
        if to_action == "manager": return 1

        if from_action in ( "member", "null" ) and to_action in ( "member", "null" ): return None
        if from_action == to_action: return None

    async def grow(
        self,
        action_holder: int,
        bring_action_for: int,
        to_role: roles
    ):
        
        _action_holder = await self.getUserByUid(action_holder)
        if not _action_holder.status == "OK": return _action_holder.create_status()

        _bring_action_for = await self.getUserByUid(bring_action_for)
        if not _bring_action_for.status == "OK": return _bring_action_for.create_status()

        _calculated = await self.calculate(
            _action_holder.user.role,
            _bring_action_for.user.role
        )

        if not _calculated == 0:
            return {
                "status": "ERROR",
                "message": "The action_holder is not able to grow bring_action (roles)"
            }
        
        opts = await self.getOption(_action_holder.user.role)
        if opts['status'] == "OK":
            if to_role in opts['option'][1]:
                self.dbs.execute("UPDATE gov_users SET role = ? WHERE uid = ?", (
                    to_role,
                    _bring_action_for.user.uid
                ))
                self.dbs.commit()
                return {
                    "status": "OK"
                }
            
            else:
                return {
                    "status": "ERROR",
                    "message": f"The action_holder is not able to grow a user into the {to_role}"
                }
        else:
            return {
                "status": "OK",
                "message": "Invalid role detected"
            }
        
    async def customOption( # Only Control by Local Admins
        self,
        role: roles,
        which: list[roles]
    ):
        ...
    
    # async def addAdmin(
    #     self,
    #     uid: int
    # ):
    #     admin = await self.getAdminByUid(uid)

    #     if admin.status == "OK":
    #         return AdminResponse({
    #             "status": "ERROR",
    #             "message": "Admin exists"
    #         })
        
    #     self.dbs.execute("INSERT INTO gov_admins (uid) VALUES (?)", (
    #         uid,
    #     ))
    #     self.dbs.commit()

    #     return AdminResponse({
    #         "status": "OK",
    #         "admin": (
    #             uid,
    #         )
    #     })
    
    # async def removeAdmin(
        
    # )
