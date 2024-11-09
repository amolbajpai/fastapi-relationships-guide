from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from pydantic import BaseModel
from typing import List

# FastAPI app initialize
app = FastAPI()

# SQLite database configuration
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model for SQLAlchemy
Base = declarative_base()

# SQLAlchemy Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True, index=True)
    bio = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'),unique=True) # Enforcing unique constraint
    user = relationship("User", back_populates="profile")

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Pydantic models for request and response
class UserCreate(BaseModel):
    name: str
    bio: str

class UserResponse(BaseModel):
    id: int
    name: str
    bio: str  # Directly include bio here for user response
    company: str = "Bharat Pvt"

    class Config:
        orm_mode = True

class ProfileCreate(BaseModel):
    bio: str
    user_id: int

class ProfileResponse(BaseModel):
    id: int
    bio: str
    user_id: int

    class Config:
        orm_mode = True

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to create a new user with profile
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Create a new User instance
    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create a new Profile instance and link it with the user
    db_profile = Profile(bio=user.bio, user_id=db_user.id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    # Return combined UserResponse with bio from Profile
    return UserResponse(id=db_user.id, name=db_user.name, bio=db_profile.bio)



# Endpoint to get all users with profiles
@app.get("/users",response_model=List[UserResponse]) # 
def read_users(db: Session = Depends(get_db)):
    # Using `joinedload` to eagerly load profiles with users
    users = db.query(User).all()

    return [
        UserResponse(
            id=user.id,
            name=user.name,
            bio=user.profile.bio if user.profile else None  # Accessing bio directly
        )
        for user in users
    ]

# Endpoint to get user and their profile by user ID
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Return User with bio from Profile
    if user.profile:
        return UserResponse(id=user.id, name=user.name, bio=user.profile.bio)
    else:
        raise HTTPException(status_code=404, detail="Profile not found")

@app.put("/users/{user_id}",response_model=UserResponse)
def update_user(user_id: int, payload: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    user.name = payload.name

    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    profile.bio = payload.bio

    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, name=user.name, bio=profile.bio)


# Endpoint to delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User not found")
    db.delete(user)
    db.commit()
    return {"message" : "User has been deleted"}

# Endpoint to create a new profile for an existing user
@app.post("/profiles/", response_model=ProfileResponse)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(User).filter(User.id == profile.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a new Profile instance
    db_profile = Profile(bio=profile.bio, user_id=profile.user_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# Endpoint to get profile by profile ID
@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def read_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# Endpoint to get profile by profile ID
@app.get("/profiles", response_model=List[ProfileResponse])
def read_all_profile(db: Session = Depends(get_db)):
    profile = db.query(Profile).all()
    print(profile)
    print("I am ")
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.get("/profiles1", response_model=List[ProfileResponse])
def read_all_profile1(db: Session = Depends(get_db)):
    profiles = db.query(Profile).all()

    # Debugging - print out profiles and their user_ids
    for profile in profiles:
        print(f"Profile ID: {profile.id}, User ID: {profile.user_id}")
    if not profiles:
        raise HTTPException(status_code=404, detail="No profiles found")

    return profiles
