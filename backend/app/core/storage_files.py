class StorageClient:
    async def upload_resume(self, content: bytes, filename: str, user_id: str):
        return {"key": filename}


def get_storage_client():
    return StorageClient()
