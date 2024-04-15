import os
from supabase import create_client, Client

class SupabaseConfig:
    """
    Configuration for the Supabase connection.
    """
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

    @classmethod
    def get_supabase_client(cls) -> Client:
        """
        Creates and returns a Supabase client instance.
        """
        url: str = cls.SUPABASE_URL
        key: str = cls.SUPABASE_SERVICE_KEY
        supabase: Client = create_client(url, key)
        return supabase

class SupabaseService:
    def __init__(self, supabase_client: Client):
        """
        Initialize the SupabaseService with a Supabase client.
        """
        self.supabase = supabase_client

    def insert_chat_history(self, username, message, response):
        """
        Inserts a new chat record into the chat_history table.
        """
        data = {"username": username, "message": message, "response": response}
        self.supabase.table("chat_history").insert(data).execute()

    def get_chat_history(self, username):
        """
        Retrieves chat history for a specific user.
        """
        return self.supabase.table("chat_history").select("*").eq("username", username).execute()

