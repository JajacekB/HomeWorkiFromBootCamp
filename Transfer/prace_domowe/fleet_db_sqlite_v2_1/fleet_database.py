from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


engine = create_engine(
    "sqlite:///fleet.db",
    connect_args={"check_same_thread": False}
)
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


