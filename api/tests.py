from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from offers.models import Offer
from core.models import Module
import datetime

class APIExtensionTests(APITestCase):
    def setUp(self):
        self.offer = Offer.objects.create(
            title="Test Offer",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=7),
            active=True
        )
        self.module = Module.objects.create(
            label="Test Module",
            icon="fa-test",
            url_name="test_url",
            is_active=True,
            order=1
        )

    def test_get_all_offers(self):
        url = reverse('get_all_offers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Offer")

    def test_get_offer_detail(self):
        url = reverse('get_offer', kwargs={'pk': self.offer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Offer")

    def test_get_all_modules(self):
        url = reverse('get_all_modules')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertTrue(any(m['label'] == "Test Module" for m in response.data))

    def test_get_module_detail(self):
        url = reverse('get_module', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], "Test Module")
