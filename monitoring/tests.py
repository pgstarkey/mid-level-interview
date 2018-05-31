from datetime import datetime

from django.test import TestCase

from .management.commands.import_csv import valid_ip, phone_number, decode_login


class ValidIPTests(TestCase):

    def test_ill_formed_ips(self):
        for ip in ['-1.2.a', 'xyz', '@.232.233.234', '1234.3456.4567.5678',
                   '256.256.256.256', '128.67.234']:
            self.assertIs(valid_ip(ip), False)

    def test_well_formed_ips(self):
        for ip in ['0.0.0.0', '255.255.255.255', '1.2.3.4', '020.045.067.099']:
            self.assertIs(valid_ip(ip), True)


class PhoneNumberTests(TestCase):

    def test_ill_formed_numbers(self):
        for string in ['fred', '@[{#~]{}~#', '1234567890', '545 373 2346',
                       '+43 756 102 3457', '0123 456']:
            self.assertEqual(phone_number(string), '')

    def test_well_formed_numbers(self):
        for string in ['012 345 6789', '01 234 56 7890',
                       '+44 (0) 123 456 789', '+abc01234567890']:
            self.assertIs(phone_number(string).startswith('0'), True)
            self.assertIs(all([c == ' ' or 0 <= int(c) <= 9
                               for c in phone_number(string)]), True)
            self.assertIs(
                len(phone_number(string).replace(' ', '')) in [10, 11], True)


class DecodeLoginTests(TestCase):

    def test_ill_formed_datetimes(self):
        for string in ['abc', '-123/456/789', '2008-11-11-11', '23:59',
                       '2018-35-45']:
            self.assertEqual(decode_login(string), '')

    def test_possible_dates(self):
        for string in ['18|07|05', '5/7/18', '2018%5/7', r'7\5\18', '7/18/05']:
            self.assertEqual(decode_login(string), datetime(2018, 5, 7))
