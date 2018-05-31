from collections import Counter, defaultdict
import csv
from datetime import datetime
from itertools import permutations
from os import path
import re
import sqlite3

from django.core.management import BaseCommand
from ....settings import BASE_DIR, DATABASES


re_email = re.compile(r'[\w.-]+@[\w.-]+\.\w+')
date = re.compile(r'')
now = datetime.now()
logins_csv = path.join(BASE_DIR, 'contextis\data\logins.csv')
database = DATABASES['default']['NAME']


def valid_ip(string):
    """
    Determine (best efforts) whether an input string represents a valid IP
    address, on the basis that it contains four octets separated by periods,
    with each octet being in the range 0 to 255.
    :param string: the input string potentially representing an IP address
    :return: whether the string is a valid IP address (boolean)
    """
    octets = string.split('.')
    try:
        return (len(octets) == 4 and all(0 <= int(octet) <= 255
                                         for octet in octets))
    except ValueError:
        return False


def phone_number(string):
    """
    Format an input string that may represent a UK phone number (STD or
    internatonal formats) on a best efforts basis.  The number is assumed to
    have a leading zero, including after any international part.  Formatting is
    5/5 for 10-digit numbers, 3/4/4 for 11-digit numbers.
    :param string: the input string potentially representing a phone number
    :return: the formatted number or en empty string is the input is not a valid
    phone number
    """
    stripped = ''.join([c for c in string if c not in ['(', ')', '+', ' ']])
    try:
        std = stripped[stripped.index('0'):]
        if len(std) == 10:
            return ' '.join([std[:5], std[5:]])
        elif len(std) == 11:
            return ' '.join([std[:3], std[3:7], std[7:]])
        else:
            return ''
    except ValueError:
        return ''


def decode_login(string):
    """
    Return the best guess at the datatime value for the server login.  Correctly
    formatted datetimes are handled first using standard conversions, then any
    other datetimes are assumed to be dates only.  The latest date in the past
    that can be formed from any combination of the three numbers extracted
    fro mthe input is assumed to be the date that was intended.
    :param string: the input string potentially representing a datetime
    :return: the datetime if valid or None otherwise
    """
    try:
        return datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # If the datetime is not encoded as expected, try to treat it as
                # a date with Y. M and D in some unknown order, and with unknown
                # delimiters.  Badly encoded datetime strings are unlikely to
                # include a time component, and if they do then attempting to
                # decode them is likely to be error-prone.
                elements = [int(e) for e in re.sub(
                    '[^\d]+', '-', string).split('-')]
                if len(elements) != 3:
                    return None
                possibilities = permutations(elements, 3)
                possible_datetimes = []
                for poss in possibilities:
                    if poss[0] < 100:
                        poss = (poss[0] + 2000, poss[1], poss[2])
                    try:
                        possible_date = datetime(*poss)
                    except ValueError:
                        continue
                    if possible_date <= now:
                        possible_datetimes.append(possible_date)
                return (sorted(possible_datetimes, reverse=True)[0]
                        if possible_datetimes else None)
            except ValueError:
                return None


class Command(BaseCommand):

    help = 'Load login history from CSV and save to database'

    def handle(self, *args, **options):
        servers = defaultdict(set)
        user_names = defaultdict(Counter)
        user_emails = defaultdict(set)
        user_phones = defaultdict(set)
        logins = set()
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        with open(logins_csv, 'r', encoding='UTF-8') as infile:
            csv_reader = csv.reader(infile)
            next(csv_reader)
            for (server, ip, user, username, contact, login) in csv_reader:
                if valid_ip(ip) and server:
                    servers[ip].add(server)
                user_names[user].update([username])
                if re_email.match(contact):
                    user_emails[user].add(contact)
                else:
                    user_phone = phone_number(contact)
                    if user_phone:
                        user_phones[user].add(phone_number(contact))
                login_datetime = decode_login(login)
                if login_datetime:
                    logins.add((user, ip, login_datetime))
        for ip in servers:
            cursor.execute('INSERT INTO servers VALUES (?, ?)',
                           (ip, list(servers[ip])[0]))
        for user in user_names:
            cursor.execute('INSERT INTO users VALUES (?, ?)',
                           (user, user_names[user].most_common(1)[0][0]))
            for email in user_emails[user]:
                cursor.execute('INSERT INTO user_emails VALUES (?, ?)',
                               (user, email))
            for phone in user_phones[user]:
                cursor.execute('INSERT INTO user_phones VALUES (?, ?)',
                               (user, phone))
        for user, ip, login_datetime in sorted(logins, key=lambda x: x[2]):
            cursor.execute('INSERT INTO logins VALUES (?, ?, ?)',
                           (user, ip, login_datetime.isoformat()))
        connection.commit()
        connection.close()
