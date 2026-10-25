from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .dependencies import get_current_user, require_admin
from .models import User, Vehicle
from .schemas import LoginInput, QuantityChange, RegisterInput, TokenOutput, UserOutput, VehicleInput, VehicleOutput, VehicleUpdate
from .security import create_access_token, hash_password, verify_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Car Dealership Inventory API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/auth/register", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(payload.password), is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/auth/login", response_model=TokenOutput)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenOutput(access_token=create_access_token(user.id), is_admin=user.is_admin)

@app.get("/api/auth/me", response_model=UserOutput)
def me(user: User = Depends(get_current_user)):
    return user

@app.get("/api/vehicles", response_model=list[VehicleOutput])
def list_vehicles(
    available_only: bool = False,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(Vehicle).order_by(Vehicle.id.desc())
    if available_only:
        stmt = stmt.where(Vehicle.quantity > 0)
    return list(db.scalars(stmt).all())

@app.get("/api/vehicles/search", response_model=list[VehicleOutput])
def search_vehicles(
    make: str | None = None,
    model: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot exceed max_price")
    stmt = select(Vehicle)
    for field, value in (("make", make), ("model", model), ("category", category)):
        if value and value.strip():
            stmt = stmt.where(getattr(Vehicle, field).ilike(f"%{value.strip()}%"))
    if min_price is not None:
        stmt = stmt.where(Vehicle.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Vehicle.price <= max_price)
    return list(db.scalars(stmt.order_by(Vehicle.id.desc())).all())

@app.post("/api/vehicles", response_model=VehicleOutput, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleInput, db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

@app.put("/api/vehicles/{vehicle_id}", response_model=VehicleOutput)
def update_vehicle(
    vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is None:
            raise HTTPException(status_code=422, detail=f"{key} cannot be null")
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise HTTPException(status_code=422, detail=f"{key} must not be blank")
        setattr(vehicle, key, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle

@app.delete("/api/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/api/vehicles/{vehicle_id}/purchase", response_model=VehicleOutput)
def purchase_vehicle(vehicle_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    # The conditional UPDATE makes stock decrement a single database operation.
    result = db.execute(
        update(Vehicle)
        .where(Vehicle.id == vehicle_id, Vehicle.quantity > 0)
        .values(quantity=Vehicle.quantity - 1)
    )
    if result.rowcount == 0:
        db.rollback()
        if not db.get(Vehicle, vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        raise HTTPException(status_code=409, detail="Vehicle is out of stock")
    db.commit()
    return db.get(Vehicle, vehicle_id)

@app.post("/api/vehicles/{vehicle_id}/restock", response_model=VehicleOutput)
def restock_vehicle(
    vehicle_id: int, payload: QuantityChange, db: Session = Depends(get_db),
    _user: User = Depends(require_admin),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle.quantity += payload.quantity
    db.commit()
    db.refresh(vehicle)
    return vehicle
