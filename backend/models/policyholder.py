import uuid
from sqlalchemy import Text, Boolean, DateTime
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin

class Policyholder(Base, TimestampMixin):
    """
    Represents the identity of the insurance customer.
    Extended to include Supabase auth_user_id and phone identity.
    """
    __tablename__ = "policyholders"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Identity linkage
    auth_user_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), unique=True, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    updated_at: Mapped[None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    policies: Mapped[list["Policy"]] = relationship("Policy", back_populates="policyholder")

    def __repr__(self) -> str:
        return f"<Policyholder id={self.id!r} auth_user_id={self.auth_user_id!r}>"
