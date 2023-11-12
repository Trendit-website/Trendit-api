import os, random, string, pathlib
from datetime import date
from werkzeug.utils import secure_filename
from flask import url_for
from PIL import Image as PillowImage
import cloudinary
import cloudinary.uploader

from app.extensions import db
from app.models.image import Image
from config import Config

cloudinary.config( 
    cloud_name = Config.CLOUDINARY_CLOUD_NAME, 
    api_key = Config.CLOUDINARY_API_KEY, 
    api_secret = Config.CLOUDINARY_API_SECRET 
)

def save_image(img_file):
    '''
    This takes an Image file,
    uploads the Image file to Cloudinary,
    and then return the image id after adding the image to Image Table
    '''
    
    # Generate a random string and append it to the original file name
    rand_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    img_name = secure_filename(img_file.filename) # Grab file name of the selected image
    the_img_name, theImgExt = os.path.splitext(os.path.basename(img_name)) # get the file name and extension
    new_img_name = f"{the_img_name}-{rand_string}"
    
    # create the path were image will be stored
    year = (str(date.today().year))
    month = (str(date.today().month).zfill(2))
    folder_path = f"{year}/{month}"
    
    # Upload the image to Cloudinary
    upload_result = cloudinary.uploader.upload(
        img_file,
        public_id = new_img_name,
        folder = folder_path,
        format = 'jpg',
        quality = 87
    )
    # Get the URLs of the uploaded image
    original_jpg = upload_result['url']
    
    # Add the image properties to database
    newImage = Image(filename=img_name, original_jpg=original_jpg)
    
    db.session.add(newImage)
    db.session.commit()
    img_id = newImage.id
    
    return img_id
