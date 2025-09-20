from datetime import datetime

from sqlalchemy import String, TIMESTAMP, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class CheckedDomains(Base):
    __tablename__ = "checked_domains"
    domain: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    tld: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(16))
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registered_to: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    checked_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now())
    source_table_name: Mapped[str] = mapped_column(String(255), index=True)
