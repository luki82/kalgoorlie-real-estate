from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Inquiry


class CleaningSiteTests(TestCase):
    def test_pages_load_with_cleaning_content(self):
        for name in ['home', 'services', 'about', 'general_contact', 'terms']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)
            self.assertNotContains(response, 'drafting', status_code=200)
            self.assertNotContains(response, 'Drafting', status_code=200)
        self.assertContains(self.client.get(reverse('home')), 'mine site cleaning')

    def test_old_portfolio_link_redirects_to_services(self):
        response = self.client.get('/portfolio/')
        self.assertRedirects(response, reverse('services'), status_code=301)

    def test_quote_form_saves_enquiry(self):
        response = self.client.post(reverse('general_contact'), {
            'full_name': 'Test Site', 'email': 'site@example.com', 'phone': '',
            'subject': 'Cleaning quote', 'message': 'Crib room and ablutions, weekly.',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Inquiry.objects.count(), 1)


class BusinessDetailsTests(TestCase):
    def test_contact_link_in_menu(self):
        self.assertContains(self.client.get(reverse('home')), 'href="/contact/">Contact</a>')

    @override_settings(PUBLIC_LIABILITY_COVER='', BUSINESS_PHONE='')
    def test_insurance_and_phone_hidden_when_not_set(self):
        response = self.client.get(reverse('general_contact'))
        self.assertNotContains(response, 'public liability')
        self.assertNotContains(response, 'tel:')

    @override_settings(PUBLIC_LIABILITY_COVER='$20 million', BUSINESS_PHONE='0400 123 456')
    def test_insurance_and_phone_shown_when_set(self):
        response = self.client.get(reverse('general_contact'))
        self.assertContains(response, '$20 million public liability insured')
        self.assertContains(response, 'href="tel:0400123456"')
