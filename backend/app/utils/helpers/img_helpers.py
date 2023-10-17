import os, random, string, pathlib
from datetime import date
from werkzeug.utils import secure_filename
from flask import url_for
from PIL import Image as PillowImage

from app.extensions import db
from app.models.image import Image
from config import Config


def save_image(img_file):
    '''
    This takes a Image file,
    saves the Image file into the UPLOADS directory,
    and then return the image id after adding the image to Image Table
    '''
    WEBP_FORMAT = 'webp'
    JPG_FORMAT = 'jpeg'
    IMAGE_QUALITY = 87
    
    # create the path were image will be stored
    year = (str(date.today().year))
    month = (str(date.today().month).zfill(2))
    date_path = os.path.join(year, month)
    webp_path = os.path.join(date_path, 'webp')
    jpg_path = os.path.join(date_path, 'jpg')
    
    pathlib.Path(Config.UPLOADS_DIR, year).mkdir(exist_ok=True)
    pathlib.Path(Config.UPLOADS_DIR, year, month).mkdir(exist_ok=True)
    pathlib.Path(Config.UPLOADS_DIR, year, month, 'webp').mkdir(exist_ok=True)
    pathlib.Path(Config.UPLOADS_DIR, year, month, 'jpg').mkdir(exist_ok=True)
    
    # Generate a random string and append it to the original file name
    rand_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    img_name = secure_filename(img_file.filename) # Grab file name of the selected image
    the_img_name, theImgExt = os.path.splitext(os.path.basename(img_name)) # get the file name and extension
    webpIMG = f"{the_img_name}-{rand_string}.webp"
    jpgIMG = f"{the_img_name}-{rand_string}.jpg"
    
    # Save the original image
    # convert the image to webp and jpg format
    with PillowImage.open(img_file) as img:
        img.convert('RGB').save(os.path.join(Config.UPLOADS_DIR, webp_path, webpIMG), WEBP_FORMAT, quality=IMAGE_QUALITY)
        img.convert('RGB').save(os.path.join(Config.UPLOADS_DIR, jpg_path, jpgIMG), JPG_FORMAT, quality=IMAGE_QUALITY)
        
        original_webp = url_for('static', filename=os.path.join("uploads", webp_path, webpIMG).replace(os.sep, '/'))
        original_jpg = url_for('static', filename=os.path.join("uploads", jpg_path, jpgIMG).replace(os.sep, '/'))
    
    # Add the image properties to database
    newImage = Image(filename=img_name, original_webp=original_webp, original_jpg=original_jpg)
    
    db.session.add(newImage)
    db.session.commit()
    img_id = newImage.id
    
    return img_id
