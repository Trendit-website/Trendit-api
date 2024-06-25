from sqlalchemy.exc import ( DataError, DatabaseError )

from ...extensions import db
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import log_exception

from ...models.social import social_media_platforms


class SocialMediaPlatformsController:
    
    @staticmethod
    def get_social_media_platforms():
        try:
            extra_data = {
                "platforms": social_media_platforms
            }
            
            api_response = success_response("Social Media Platforms Fetch successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred fetching social media platforms", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response
