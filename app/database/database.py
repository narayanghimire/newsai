import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ensure the data directory exists
db_path = 'data'
if not os.path.exists(db_path):
    os.makedirs(db_path)

# Load database name from environment variable or use default
db_file_name = os.getenv('DB_NAME', 'newsai.db')
DATABASE_URL = f'sqlite:///{db_path}/{db_file_name}'

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
