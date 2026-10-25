from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool

class UserOutput(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool

class VehicleInput(BaseModel):
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)

    @field_validator("make", "model", "category")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")
        return value

class VehicleUpdate(BaseModel):
    make: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)

class VehicleOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    make: str
    model: str
    category: str
    price: float
    quantity: int

class QuantityChange(BaseModel):
    quantity: int = Field(gt=0)
