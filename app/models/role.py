# =====================================================================
# FILE: app/models/role.py
# =====================================================================

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import user_roles

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Many-to-many relationship with User
    users = relationship("User", secondary=user_roles, back_populates="roles")
