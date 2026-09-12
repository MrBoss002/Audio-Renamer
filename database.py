from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self._db = self._client[database_name]
        self._users = self._db["users"]

    async def add_user(self, user_id: int):
        """Adds a new user to the database if they don't already exist."""
        if not await self.is_user_exist(user_id):
            user_doc = {
                "_id": user_id,
                "thumbnail": None,
                "caption": None,
                "audio_title": None,
                "artist_name": None
            }
            await self._users.insert_one(user_doc)

    async def is_user_exist(self, user_id: int) -> bool:
        """Checks if a user exists in the database."""
        user = await self._users.find_one({"_id": user_id})
        return bool(user)

    async def total_users_count(self) -> int:
        """Returns the total number of unique users."""
        return await self._users.count_documents({})

    async def get_user_settings(self, user_id: int) -> dict:
        """Retrieves all customized settings for a specific user."""
        user = await self._users.find_one({"_id": user_id})
        if user:
            return {
                "thumbnail": user.get("thumbnail"),
                "caption": user.get("caption"),
                "audio_title": user.get("audio_title"),
                "artist_name": user.get("artist_name")
            }
        return {"thumbnail": None, "caption": None, "audio_title": None, "artist_name": None}

    async def update_setting(self, user_id: int, key: str, value):
        """Updates a specific user setting (thumbnail, caption, audio_title, artist_name)."""
        await self._users.update_one({"_id": user_id}, {"$set": {key: value}})

    async def delete_setting(self, user_id: int, key: str):
        """Clears/resets a specific user setting back to None."""
        await self._users.update_one({"_id": user_id}, {"$set": {key: None}})

    async def get_all_users(self):
        """Returns a cursor/list of all user documents for broadcasting."""
        return self._users.find({})

db = Database(Config.MONGO_URI, Config.DB_NAME)
