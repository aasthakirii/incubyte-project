from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_vehicle_price_nonnegative"),
        CheckConstraint("quantity >= 0", name="ck_vehicle_quantity_nonnegative"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    make: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
