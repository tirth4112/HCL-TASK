from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, MetaData, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
from .config import DATABASE_URL

Base = declarative_base()

class PolicyRule(Base):
    __tablename__ = 'policy_rules'
    id = Column(Integer, primary_key=True)
    policy_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    policy_text = Column(Text, nullable=False)
    metadata_col = Column(JSON, nullable=True)
    embedding = Column(JSON) # Using 384 for all-MiniLM-L6-v2
    created_at = Column(DateTime, default=datetime.utcnow)

class Claim(Base):
    __tablename__ = 'claims'
    id = Column(Integer, primary_key=True)
    claim_id = Column(String, unique=True, nullable=False)
    employee_name = Column(String)
    trip_start = Column(String)
    trip_end = Column(String)
    submitted_date = Column(String)
    total_claimed = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClaimItem(Base):
    __tablename__ = 'claim_items'
    id = Column(Integer, primary_key=True)
    claim_id = Column(String, nullable=False)
    category = Column(String)
    description = Column(String)
    amount = Column(Float)
    receipt_attached = Column(Integer) # sqlite/postgres compat for bool usually boolean but we use integer or bool

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    claim_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_node = Column(String)
    tool_name = Column(String)
    input_data = Column(JSON)
    output_data = Column(JSON)

class DatabaseManager:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def setup_database(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()
