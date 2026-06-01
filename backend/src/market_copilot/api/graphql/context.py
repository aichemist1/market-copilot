from __future__ import annotations

from dataclasses import dataclass

from strawberry.fastapi import BaseContext
from sqlalchemy.orm import Session


@dataclass
class GraphQLContext(BaseContext):
    db: Session
    user_profile: str
