'''
This module defines helper functions for handling media operations in the Trendit³ Flask application.

These functions assist with tasks such as saving media files to Cloudinary and adding media properties to the database.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
import os
from io import BufferedReader
import tempfile
from datetime import date
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import cloudinary
import cloudinary.uploader

from app.extensions import db
from app.models import Media
from config import Config
from .basic_helpers import console_log, log_exception, generate_random_string

cloudinary.config( 
    cloud_name = Config.CLOUDINARY_CLOUD_NAME, 
    api_key = Config.CLOUDINARY_API_KEY, 
    api_secret = Config.CLOUDINARY_API_SECRET 
)

# Constants for file type validation
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.svg'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.flv'}

def get_folder_path():
    """Generate the folder path based on the current date."""
    year = str(date.today().year)
    month = str(date.today().month).zfill(2)
    return f"{year}/{month}"

def validate_file_extension(extension):
    """Validate the file extension and determine resource type."""
    if extension.lower() in IMAGE_EXTENSIONS:
        return "image"
    elif extension.lower() in VIDEO_EXTENSIONS:
        return "video"
    else:
        raise ValueError("Invalid file type")

def upload_to_cloudinary(media_file: FileStorage, new_media_name, folder_path, resource_type):
    """Upload the media file to Cloudinary."""
    try:
        return cloudinary.uploader.upload(
            media_file,
            resource_type=resource_type,
            public_id=new_media_name,
            folder=folder_path,
        )
    except Exception as e:
        log_exception("Cloudinary upload failed", e)
        raise e
    

def save_media_to_db(media_name: str, original_media_path: str):
    """Save the media record to the database."""
    try:
        new_media = Media(filename=media_name, media_path=original_media_path)
        db.session.add(new_media)
        db.session.commit()
        return new_media
    except Exception as e:
        db.session.rollback()
        log_exception("Database commit failed", e)
        raise e


def save_media(media_file, filename=None) -> Media:
    """
    Saves a media file (image or video) to Cloudinary and the database.
    and then return the media instance after adding the media to Media Table

    Args:
        media_file (werkzeug.datastructures.FileStorage): The media file object to be uploaded.

    Returns:
        Media: The Media instance of the saved media in the database.

    Raises:
        ValueError: If the file type is not supported.
    """
    
    console_log("media_file", media_file)
    
    
    # Generate a random string and append it to the original file name
    rand_string = generate_random_string(8)
    media_name = secure_filename(filename) if filename else secure_filename(media_file.filename) # Grab file name of the selected media
    the_media_name, the_media_ext = os.path.splitext(os.path.basename(media_name)) # get the file name and extension
    new_media_name = f"{the_media_name}-{rand_string}"
    
    
    folder_path = get_folder_path() # create the path were image will be stored
    resource_type = validate_file_extension(the_media_ext) # Check the file type and set the resource_type accordingly
    
    # Upload the media to Cloudinary
    upload_result = upload_to_cloudinary(media_file, new_media_name, folder_path, resource_type)
    
    original_media_path = upload_result['secure_url'] # Get the URL of the uploaded media
    
    # Add the media properties to database
    new_media = save_media_to_db(media_name, original_media_path)
    
    return new_media


def save_media_files_to_temp(media_files):
    temp_dir = tempfile.mkdtemp()
    media_file_paths = []
    
    console_log("media files", media_files)
    if isinstance(media_files, list):
        
        for media_file in media_files:
            filename = secure_filename(media_file.filename)
            file_path = os.path.join(temp_dir, filename)
            media_file.save(file_path)
            media_file_paths.append(file_path)
    else:
        media_file = media_files
        filename = secure_filename(media_file.filename)
        file_path = os.path.join(temp_dir, filename)
        media_file.save(file_path)
        media_file_paths.append(file_path)

    return media_file_paths