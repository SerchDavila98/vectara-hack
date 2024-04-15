from datetime import datetime
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
class ChatHistory:
    def __init__(self, username: str, message: str, response: str, timestamp: datetime = None):
        """
        Initialize a new ChatHistory record.
        
        Args:
            username (str): The username of the user.
            message (str): The message sent by the user.
            response (str): The chatbot's response to the user's message.
            timestamp (datetime, optional): The timestamp of when the message was sent. Defaults to current time.
        """
        self.username = username
        self.message = message
        self.response = response
        self.timestamp = timestamp if timestamp is not None else datetime.now()

    def __repr__(self):
        """
        Returns a string representation of the ChatHistory record.
        """
        return f"<ChatHistory(username='{self.username}', message='{self.message}', response='{self.response}', timestamp='{self.timestamp}')>"

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    message = Column(String, nullable=False)
    response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChatHistory(username='{self.username}', message='{self.message}', response='{self.response}', timestamp='{self.timestamp}')>"


# Creating an engine instance
engine = create_engine(DATABASE_URL, echo=True)

# Creating a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creating tables
Base.metadata.create_all(bind=engine)
