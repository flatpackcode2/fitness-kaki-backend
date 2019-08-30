#At the moment, we do not have a separate image database as there is no image gallery feature

from models.user import User
from models.event import Event
from utils.im_helpers import upload_to_s3
from flask import make_response, request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

images_api_blueprint = Blueprint('images_api', __name__)

@images_api_blueprint.route('/profile', methods=['POST'])
@jwt_required
def profile():
    current_user = get_jwt_identity()
    user = User.get_by_id(current_user)

    image_file= request.files.get('image_file', None)
    image_file.filename = secure_filename(image_file.filename)

    if image_file:
        output = upload_to_s3(image_file)
        query = User.update(profile_image=image_file.filename).where(User.id==current_user)
        query.execute() #no validation if update goes wrongly
        
        response = {'message':'profile image updated successfully', 'image_url':output}

        return make_response(jsonify(response),200)

# #need to work this out
# @images_api_blueprint.route('/event', methods=['POST'])
# @jwt_required
# def profile():
#     current_user = get_jwt_identity()
#     user = User.get_by_id(current_user)

#     image_file= request.files.get('image_file', None)
#     image_file.filename = secure_filename(image_file.filename)

#     if image_file:
#         output = upload_to_s3(image_file)
#         query = Event.update(Event.event_image).where(User.id==current_user)
#         query.execute() #no validation if update goes wrongly
        
#         response = {'message':'profile image updated successfully', 'image_url':output}

#         return make_response(jsonify(response),200)


    