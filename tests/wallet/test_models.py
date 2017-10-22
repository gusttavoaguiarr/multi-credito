from multi_credit import app, db
import unittest
import json
from tests.helpers import TestHelper


class WalletModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.from_object('multi_credit.config.TestingConfig')
        self.client = self.app.test_client()

        self.wallet_data = {
            "max_limit": 0,
            "user_limit": 0,
            "credit": 0,
            "user_id": 1
        }

        self.wallet_return = {
            "wallet": {
                "credit": 0,
                "id": 1,
                "max_limit": 0,
                "user_id": 1,
                "user_limit": 0
            }
        }

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_create_wallet(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        response = self.client.post(
            '/api/v1/wallet',
            data=json.dumps(self.wallet_data),
            headers=headers)
        result = json.loads(response.data.decode())

        self.assertEqual(
            result['message'], "New wallet created!")
        self.assertEqual(response.status_code, 201)

    def test_registered_with_already_registered_wallet(self):

        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        self.client.post(
            '/api/v1/wallet',
            data=json.dumps(self.wallet_data),
            headers=headers)

        response = self.client.post(
            '/api/v1/wallet',
            data=json.dumps(self.wallet_data),
            headers=headers)
        result = json.loads(response.data.decode())

        self.assertEqual(
            result['message'], "Wallet already exists!")
        self.assertEqual(response.status_code, 200)

    def test_get_wallet(self):
        TestHelper().create_user(self.client)
        response_sign_in = TestHelper().sign_in(self.client)
        auth_token = json.loads(response_sign_in.data.decode())

        headers = TestHelper().headers
        headers['x-access-token'] = auth_token['token']

        self.client.post(
            '/api/v1/wallet',
            data=json.dumps(self.wallet_data),
            headers=headers)

        response_wallet = self.client.get(
            '/api/v1/wallet',
            headers=headers)
        response_message = json.loads(response_wallet.data.decode())
        self.assertEqual(response_message, self.wallet_return)
        self.assertEqual(response_wallet.status_code, 201)
