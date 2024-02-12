'''
This module defines helper functions for handling media operations in the Trendit³ Flask application.

These functions assist with tasks such as saving media files to Cloudinary and adding media properties to the database.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
import os, random, string
from datetime import date
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

from app.extensions import db
from app.models import Media
from config import Config

cloudinary.config( 
    cloud_name = Config.CLOUDINARY_CLOUD_NAME, 
    api_key = Config.CLOUDINARY_API_KEY, 
    api_secret = Config.CLOUDINARY_API_SECRET 
)

def save_media(media_file):
    """
    Saves a media file (image or video) to Cloudinary and the database.
    and then return the media id after adding the media to Media Table

    Args:
        media_file: The media file object to be uploaded.

    Returns:
        int: The ID of the saved media in the database.

    Raises:
        ValueError: If the file type is not supported.
    """
    
    # Generate a random string and append it to the original file name
    rand_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    media_name = secure_filename(media_file.filename) # Grab file name of the selected media
    the_media_name, theMediaExt = os.path.splitext(os.path.basename(media_name)) # get the file name and extension
    new_media_name = f"{the_media_name}-{rand_string}"
    
    
    # create the path were image will be stored
    year = (str(date.today().year))
    month = (str(date.today().month).zfill(2))
    folder_path = f"{year}/{month}"
    
    
    # Check the file type and set the resource_type accordingly
    if theMediaExt.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
        resource_type = "image"
    elif theMediaExt.lower() in ['.mp4', '.avi', '.mov', '.flv']:
        resource_type = "video"
    else:
        raise ValueError("Invalid file type")
    
    # Upload the media to Cloudinary
    upload_result = cloudinary.uploader.upload(
        media_file,
        resource_type = resource_type,
        public_id = new_media_name,
        folder = folder_path,
    )
    # Get the URL of the uploaded media
    original_media_path = upload_result['url']
    
    # Add the media properties to database
    newMedia = Media(filename=media_name, media_path=original_media_path)
    
    db.session.add(newMedia)
    db.session.commit()
    media_id = newMedia.id
    
    return media_id
