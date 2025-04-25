
import os
import pymssql
import time
from typing import List, Dict, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure SQL Database connection parameters
# These should be set as environment variables in production
SQL_SERVER = os.environ.get("SQL_SERVER", "your-server.database.windows.net")
SQL_DATABASE = os.environ.get("SQL_DATABASE", "your-database")
SQL_USERNAME = os.environ.get("SQL_USERNAME", "your-username")
SQL_PASSWORD = os.environ.get("SQL_PASSWORD", "your-password")

def get_db_connection():
    """Create a connection to Azure SQL Database using pymssql."""
    try:
        # Connect to the Azure SQL database
        conn = pymssql.connect(
            server=SQL_SERVER,
            user=SQL_USERNAME,
            password=SQL_PASSWORD,
            database=SQL_DATABASE
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return None

def initialize_chat_history_table():
    """Create the chat_history table if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        logger.warning("Failed to initialize chat history table: No database connection")
        return False

    try:
        cursor = conn.cursor()
        
        # Check if the table exists first
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'chat_history')
        BEGIN
            CREATE TABLE chat_history (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(255),
                user_message NVARCHAR(MAX),
                ai_response NVARCHAR(MAX),
                timestamp DATETIME2 DEFAULT GETDATE(),
                session_id NVARCHAR(255),
                endpoint_used NVARCHAR(255),
                processing_time FLOAT,
                tokens_used INT,
                user_feedback NVARCHAR(50),
                metadata NVARCHAR(MAX)
            )
        END
        """)
        conn.commit()
        logger.info("Chat history table initialization completed")
        return True
    except Exception as e:
        logger.error(f"Error initializing chat history table: {str(e)}")
        return False
    finally:
        conn.close()

def log_chat_interaction(user_id: str, user_message: str, ai_response: str, 
                         endpoint_used: str = None, processing_time: float = 0.0, 
                         tokens_used: int = 0, session_id: str = None, metadata: Dict = None):
    """Log a chat interaction to the database."""
    conn = get_db_connection()
    if not conn:
        logger.warning("Failed to log chat interaction: No database connection")
        return False

    try:
        cursor = conn.cursor()
        metadata_str = str(metadata) if metadata else None
        
        # Insert the chat interaction into the database
        cursor.execute("""
        INSERT INTO chat_history 
        (user_id, user_message, ai_response, endpoint_used, processing_time, tokens_used, session_id, metadata) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, user_message, ai_response, endpoint_used, processing_time, tokens_used, session_id, metadata_str))
        
        conn.commit()
        logger.info(f"Chat interaction logged for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error logging chat interaction: {str(e)}")
        return False
    finally:
        conn.close()

def get_user_chat_history(user_id: str, limit: int = 50) -> List[Dict]:
    """Get a user's chat history."""
    conn = get_db_connection()
    if not conn:
        logger.warning("Failed to get user chat history: No database connection")
        return []

    try:
        cursor = conn.cursor(as_dict=True)
        
        # Get the user's chat history
        cursor.execute("""
        SELECT TOP %d id, user_message, ai_response, timestamp, endpoint_used, processing_time
        FROM chat_history
        WHERE user_id = %s
        ORDER BY timestamp DESC
        """, (limit, user_id))
        
        history = cursor.fetchall()
        return history
    except Exception as e:
        logger.error(f"Error getting user chat history: {str(e)}")
        return []
    finally:
        conn.close()

# Initialize the table when the module is imported
# Comment this out if you want to manually control initialization
# initialize_chat_history_table()
