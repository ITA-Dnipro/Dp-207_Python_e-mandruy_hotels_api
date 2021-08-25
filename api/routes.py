from flask import Blueprint, request, jsonify
from .parser import Scraper, SomeProblemWithParsing, CityNotExists
from marshmallow import Schema, fields, validate
from .utils.api_jwt import check_token


# create schema for hotel responce
class HotelSchema(Schema):
    hotel_name = fields.Str(required=True, validate=validate.Length(max=150))
    city = fields.Str(required=True, validate=validate.Length(max=100))
    adress = fields.Str(required=True)
    photo = fields.Str()
    detail = fields.Str()
    prices = fields.Dict()
    contacts = fields.Str()
    href = fields.Str(validate=validate.Length(max=100))


class HotelSchemaForOrder(Schema):
    prices = fields.Dict()


hotels_schema = HotelSchema(many=True)
hotel_schema = HotelSchemaForOrder()

# create blueprint for api
api_blu = Blueprint('api', __name__, url_prefix='/api')


# create endpoint to get all hotels by city
@api_blu.route('/get_all_hotels', methods=['POST'])
@check_token
def get_all_hotels():
    if not request.get_json():
        return jsonify({'msg': 'wrong request'}), 403
    try:
        data = Scraper(**request.get_json()).parse()
        result = hotels_schema.loads(data)
        return jsonify(result), 200
    except SomeProblemWithParsing as e:
        return jsonify({'msg': e.msg}), 500
    except CityNotExists as e:
        return jsonify({'msg': e.msg}), 404

# create endpoint to get data for free rooms in hotel by date


@api_blu.route('/get_hotel_rooms', methods=['POST'])
@check_token
def get_hotel_rooms():

    if not request.get_json():
        return jsonify({'msg': 'wrong request'}), 403

    try:
        data = Scraper(**request.get_json()).parse()
        result = hotel_schema.loads(data)
        return jsonify(result), 200
    except SomeProblemWithParsing as e:
        return jsonify({'msg': e.msg}), 500
