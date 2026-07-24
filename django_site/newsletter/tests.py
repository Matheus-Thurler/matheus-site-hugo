import base64
import json

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Subscriber


@override_settings(
    NEWSLETTER_SEND_WELCOME=False,
    NEWSLETTER_INTERNAL_TOKEN='test-token',
    RATELIMIT_ENABLE=False,
)
class SubscribeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('newsletter:subscribe')

    def test_subscribe_success(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'email': 'user@example.com', 'name': 'User'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'subscribed')
        self.assertTrue(Subscriber.objects.filter(email='user@example.com').exists())

    def test_subscribe_duplicate(self):
        Subscriber.objects.create(email='user@example.com', name='User')
        response = self.client.post(
            self.url,
            data=json.dumps({'email': 'user@example.com', 'name': 'User'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'already subscribed')

    def test_subscribe_invalid_email(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'email': 'not-an-email', 'name': 'User'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_subscribe_missing_name(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'email': 'user@example.com'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


@override_settings(NEWSLETTER_INTERNAL_TOKEN='test-token')
class UnsubscribeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.subscriber = Subscriber.objects.create(email='user@example.com', name='User')

    def test_unsubscribe(self):
        token = base64.urlsafe_b64encode(b'user@example.com').decode()
        response = self.client.get(reverse('newsletter:unsubscribe'), {'token': token})
        self.assertEqual(response.status_code, 200)
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)


@override_settings(NEWSLETTER_INTERNAL_TOKEN='test-token')
class SubscribersApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        Subscriber.objects.create(email='a@example.com', name='A')
        Subscriber.objects.create(email='b@example.com', name='B', is_active=False)

    def test_subscribers_api_requires_token(self):
        response = self.client.get(reverse('newsletter:subscribers_api'))
        self.assertEqual(response.status_code, 401)

    def test_subscribers_api_returns_active_only(self):
        response = self.client.get(
            reverse('newsletter:subscribers_api'),
            HTTP_X_INTERNAL_TOKEN='test-token',
        )
        self.assertEqual(response.status_code, 200)
        emails = [s['email'] for s in response.json()['subscribers']]
        self.assertEqual(emails, ['a@example.com'])
