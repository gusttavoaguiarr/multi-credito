from multi_credit import app, db
import unittest
import json
from tests.helpers import TestHelper
from multi_credit.wallet.models import Wallet


class CardModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.from_object('multi_credit.config.TestingConfig')
        self.client = self.app.test_client()

        self.card_data = {
            "number": 5165834017829286,
            "expiration_date": "2018-07-5",
            "validity_date": "2017-07-5",
            "cvv": 408,
            "limit": 2000
        }

        self.card_return = {
            "card": {
                "credit": 2000,
                "cvv": "408",
                "expiration_date": "Thu, 05 Jul 2018 00:00:00 GMT",
                "id": 1,
                "limit": 2000,
                "name": "GUSTAVO D F AGUIAR",
                "number": 5165834017829286,
                "validity_date": "Wed, 05 Jul 2017 00:00:00 GMT",
                "wallet_id": 1
            }
        }

        self.wallet_data = {
            "max_limit": 0,
            "user_limit": 0,
            "spent_credit": 0,
            "user_id": 1
        }

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_create_card(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        response = self.client.post(
            '/api/v1/card',
            data=json.dumps(self.card_data),
            headers=headers)
        result = json.loads(response.data.decode())

        with self.app.app_context():
            wallet = Wallet.query.filter_by(user_id=1).first()

        self.assertEqual(
            wallet.max_limit, 2000.00)
        self.assertEqual(
            result['message'], "New card created!")
        self.assertEqual(response.status_code, 201)

    def test_get_one_card(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        self.client.post(
            '/api/v1/wallet',
            data=json.dumps(self.wallet_data),
            headers=headers)

        self.client.post(
            '/api/v1/card',
            data=json.dumps(self.card_data),
            headers=headers)

        response_card = self.client.get(
            '/api/v1/card/1',
            headers=headers)
        response_message = json.loads(response_card.data.decode())
        self.assertEqual(response_message, self.card_return)
        self.assertEqual(response_card.status_code, 201)

    def test_get_cards(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        self.client.post(
            '/api/v1/card',
            data=json.dumps(self.card_data),
            headers=headers)

        response_card = self.client.get(
            '/api/v1/cards',
            headers=headers)
        response_message = json.loads(response_card.data.decode())
        self.assertGreater(len(response_message['cards']), 0)
        self.assertEqual(response_card.status_code, 201)

    def test_delete_card(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        self.client.post(
            '/api/v1/wallet',
            data=json.dumps(self.wallet_data),
            headers=headers)

        self.client.post(
            '/api/v1/card',
            data=json.dumps(self.card_data),
            headers=headers)

        response = self.client.delete(
            '/api/v1/card/1',
            headers=headers)

        result = json.loads(response.data.decode())

        with self.app.app_context():
            wallet = Wallet.query.filter_by(user_id=1).first()

        self.assertEqual(
            wallet.max_limit, 0.0)
        self.assertEqual(
            result['message'], "The card has been deleted!")
        self.assertEqual(response.status_code, 200)

    def test_delete_the_card_does_not_exist(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        self.client.post(
            '/api/v1/wallet',
            data=json.dumps(self.wallet_data),
            headers=headers)

        response = self.client.delete(
            '/api/v1/card/1',
            headers=headers)

        result = json.loads(response.data.decode())

        self.assertEqual(
            result['message'], "No card found!")
        self.assertEqual(response.status_code, 200)

    def test_pay_card(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        self.client.post(
            '/api/v1/card',
            data=json.dumps(self.card_data),
            headers=headers)

        self.client.put(
            '/api/v1/wallet/buy',
            data=json.dumps({
                'value': 500,
                'date': '2017-05-10'
            }),
            headers=headers)

        self.client.put(
            '/api/v1/card/pay/1',
            data=json.dumps({
                'value_pay': 300
            }),
            headers=headers)

        response_card = self.client.get(
            '/api/v1/card/1',
            headers=headers)
        response_message = json.loads(response_card.data.decode())

        self.assertEqual(response_message['card']['credit'], 1800.0)
        self.assertEqual(response_card.status_code, 201)
