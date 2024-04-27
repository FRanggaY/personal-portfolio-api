from fastapi import File
import uuid
import os
from datetime import datetime
from pathlib import Path
import shutil


async def validation_file(file: File, limit_file_size_mb: int = 5, allowed_extension: list = ["image/jpeg", "image/png"]):
    file.file.seek(0, 2)
    file_size = file.file.tell()

    # move the cursor back to the beginning
    await file.seek(0)
    if file_size > limit_file_size_mb * 1024 * 1024:
        # more than 5 MB
        raise ValueError(f"Image too large. only allow file lower than {limit_file_size_mb} mb")

    # check the content type (MIME type)
    content_type = file.content_type
    if content_type not in allowed_extension:
        file_formats = ', '.join([mime.split('/')[-1] for mime in allowed_extension])
        raise ValueError(f"Invalid file file type. only allow file with type {file_formats}")

def upload_file(data, folder, file_extension, name = None):
    if data:
        # Generate a new filename based on date now with random uuid and provided extension
        current_date = datetime.now().date()
        new_filename = f"{name}.{file_extension}" if name else f"{current_date}-{str(uuid.uuid4())}.{file_extension}"

        # Save the uploaded file to a directory
        file_path = Path(folder) / new_filename
        with open(file_path, "wb") as f_dest:
            shutil.copyfileobj(data.file, f_dest)

        # Return the filename
        return str(Path(new_filename))
    else:
        print('error to upload file')
        return None

def delete_file(file_path: str):
    try:
        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False  # File not found
    except Exception as e:
        print(e)
        return False  # Error occurred while deleting
