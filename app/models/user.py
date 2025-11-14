# =====================================================================
# FILE: app/models/user.py
# =====================================================================

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

# Association table for many-to-many relationship between users and roles
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user") # Simple role system
    
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=True)

    # Many-to-many relationship with Role
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    department = relationship("Department", backref="users")
    division = relationship("Division", backref="users")
