from unittest.mock import patch
import pytest
import jwt
import datetime
import os
import json


def create_jwt_token():
    hotels_app_jwt_secret = os.environ.get('HOTELS_APP_JWT_SECRET_KEY')
    payload = {
        "exp": datetime.datetime.now(),
        "city_name": 'Киев',
    }
    token = jwt.encode(payload, hotels_app_jwt_secret, algorithm="HS256")
    return {'Authorization': token}


@patch('flask_hotels_service.api.parser.Scraper.parse',
       return_value=json.dumps([{"hotel_name": "BOOM",
                                 "city": "Kiev",
                                 "adress": "dfsdfsdf"}], ensure_ascii=False))
def test_response(mock, client):
    headers = create_jwt_token()
    res = client.post('/api/get_all_hotels', json={"city": 'Киев'}, headers=headers)
    assert res.status_code == 200
    assert b'city' in res.data

