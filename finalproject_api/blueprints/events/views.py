from flask import Flask, Blueprint, jsonify, make_response, request
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.event import Event
from models.user import User
from models.guestlist import Guestlist
from flask_login import current_user
from utils.im_helpers import upload_to_s3

events_api_blueprint = Blueprint('events_api', __name__)

@events_api_blueprint.route('/', methods=['POST'])
@jwt_required
def create():
    print('event_created')
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    host = get_jwt_identity()
    time = request.form.get('time')
    max_number= request.form.get('max_number')
    image_file= request.files.get('image_file')
    image_file.filename = secure_filename(image_file.filename)
    output = upload_to_s3(file=image_file)
    event =Event(name=name, description=description, location=location, host=host, time=time, max_number=max_number, event_image=image_file.filename)

    if event.save():
        print('event saved')
        event = Event.get_by_id(event.id)
        response = {'message': 'Event successfully created',
                    'data': {
                        'name':event.name,
                        'description':event.description,
                        'location': event.location,
                        'host':event.host.id,
                        'max_number':event.max_number,
                        'time':event.time
                    }}
        return make_response(jsonify(response), 200)
    else:
        response = {'message': 'Event creation failed', 'errors':event.errors}
        return make_response(jsonify(response), 400)

#retrieve a list of all events
@events_api_blueprint.route('/', methods=['GET'])
# @jwt_required
def index():
    response=[]
    events = Event.select().order_by(Event.time.desc())

    for event in events:
        data={
                'id':event.id,
                'name':event.name,
                'description':event.description,
                'location': event.location,
                'max_number':event.max_number,
                'time':event.time,
                'image':event.event_image_url}
        
        #obtain names of host, guests and provide in event
        host = {'id':event.host.id, 'username':event.host.username, 'profile_image_url':event.host.profile_image_url}
        data['host'] = host
        guestlistExists = Guestlist.get_or_none(Guestlist.event == event.id)
        roster=[]
        if guestlistExists!=None:
            guestlist = User.select().join(Guestlist, on=(Guestlist.guest == User.id)).where(Guestlist.event == event.id)
            for entry in guestlist:
                roster.append(entry.id)        
        data['guests']=roster
        response.append(data)
    return make_response(jsonify(response), 200)

