from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Announcement, Session
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from schema import CreateAnnouncement, UpdateAnnouncement

app = Flask('app')


class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({'error': error.message})
    response.status_code = error.status_code
    return response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response):
    request.session.close()
    return response


def validate_json(schema_class, json_data):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop('ctx', None)
        raise HttpError(400, error)


def get_ann_by_id(ann_id: int):
    announcement = request.session.get(Announcement, ann_id)
    if announcement is None:
        raise HttpError(status_code=404, message="Announcement not found")
    return announcement


def add_announcement(announcement: Announcement):
    try:
        request.session.add(announcement)
        request.session.commit()
    except IntegrityError:
        raise HttpError(status_code=409, message="Announcement already exists")


class AnnouncementView(MethodView):

    @property
    def session(self) -> Session:
        return request.session

    def get(self, ann_id):
        announcement = get_ann_by_id(ann_id)
        return jsonify(announcement.dict)

    def post(self):
        json_data = validate_json(CreateAnnouncement, request.json)
        announcement = Announcement(**json_data)
        add_announcement(announcement)
        return jsonify({'id': announcement.id})

    def patch(self, ann_id):
        json_data = validate_json(UpdateAnnouncement, request.json)
        announcement = get_ann_by_id(ann_id)
        for field, value in json_data.items():
            setattr(announcement, field, value)
        add_announcement(announcement)
        return jsonify(announcement.dict)

    def delete(self, ann_id):
        announcement = get_ann_by_id(ann_id)
        self.session.delete(announcement)
        self.session.commit()
        return jsonify({'status': 'deleted'})


announcement_view = AnnouncementView.as_view('announcement_view')

app.add_url_rule('/announcement/', view_func=announcement_view, methods=['POST'])
app.add_url_rule('/announcement/<int:ann_id>/', view_func=announcement_view,
                 methods=['GET', 'PATCH', 'DELETE'])

if __name__ == '__main__':
    app.run()
