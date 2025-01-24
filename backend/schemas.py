from pydantic import BaseModel
from typing import Optional, Dict, List

class ChatStateCreate(BaseModel):
    project_id: int
    solution_name: str
    messages: List[dict]

class ChatStateResponse(BaseModel):
    project_id: int
    solution_name: str
    messages: List[dict]


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass

class LoginRequest(BaseModel):
    username: str
    password: str

class Project(ProjectBase):
    id: int
    environment_spec: Optional[str] = None
    system_spec: Optional[str] = None
    safety_property: Optional[str] = None
    config: Optional[Dict] = None

    class Config:
        orm_mode = True

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    environment_spec: Optional[str] = None
    system_spec: Optional[str] = None
    safety_property: Optional[str] = None
    config: Optional[Dict] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    organization: str


class User(UserBase):
    id: int
    projects: List[Project] = []

    class Config:
        orm_mode = True


class SpecModel(BaseModel):
    content: str
