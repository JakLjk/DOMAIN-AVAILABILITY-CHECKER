from datetime import datetime

from sqlalchemy import String, TIMESTAMP, func, DateTime, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass

def initialise_domains_table(table_name:str):
    class DomainsTable(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        domain: Mapped[str] = mapped_column(String(255), primary_key=True, nullable=False)
        frequency: Mapped[int] = mapped_column(Integer, nullable=False)
        domain_punycode: Mapped[str] = mapped_column(String(255), nullable=True)
        domain_ascii: Mapped[str] = mapped_column(String(255), nullable=True)
        status: Mapped[str] = mapped_column(String(16), nullable=True)
        registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
        registered_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
        was_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
        checked_at: Mapped[datetime] = mapped_column(
            TIMESTAMP(timezone=True), server_default=func.now(),
            nullable=True)
        error_message: Mapped[str] = mapped_column(String(), nullable=True)

    return DomainsTable