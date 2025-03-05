import fastapi
from fastapi.security import OAuth2PasswordRequestForm

router = fastapi.APIRouter()

@router.get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    # get user by id
    return {}

@router.get("/groups/")
def get_groups() -> dict:
    # get list of groups
    return {}

@router.get("/groups/{group_id}/members")
def get_group_members(group_id: int) -> dict:
    # get users by group id
    return {}

@router.post("/groups/{group_id}/members")
def add_group_member(group_id: int, user: dict) -> dict:
    # add user to group
    return {}

@router.delete("/groups/{group_id}/members/{user_id}")
def remove_group_member(group_id: int, user_id: int) -> dict:
    # remove user from group
    return {}

@router.get("/roles/")
def get_roles() -> dict:
    # get list of roles
    return {}

@router.get("/roles/{role_id}")
def get_role(role_id: int) -> dict:
    # get role by id
    return {}

@router.post("/roles/")
def create_role(role: dict) -> dict:
    # create role
    return {}

@router.put("/roles/{role_id}")
def update_role(role_id: int, role: dict) -> dict:
    # update role by id
    return {}
