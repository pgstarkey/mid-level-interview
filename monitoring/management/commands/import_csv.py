"""
Module to import CSV file in isolation
"""

from collections import Counter, defaultdict
import csv
from datetime import datetime
from itertools import permutations
from os import path
import re
import sqlite3


re_email = re.compile(r'[\w.-]+@[\w.-]+\.\w+')
date = re.compile(r'')
now = datetime.now()


def valid_ip(string):
    octets = string.split('.')
    return len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets)


def phone_number(string):
    stripped = ''.join([c for c in string if c not in ['(', ')', '+', ' ']])
    try:
        std = stripped[stripped.index('0'):]
        return (' '.join([std[:5], std[5:]]) if len(std) == 10 else
                ' '.join([std[:3], std[3:7], std[7:]]))
    except ValueError:
        return ''


def decode_login(string):
    print("Decoding", string)
    try:
        return datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            elements = [int(e) for e in re.sub(
                '[^\d]+', '-', string).split('-')]
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
            return sorted(possible_datetimes, reverse=True)[0]


def main():

    root = r'C:\Users\Paul\PycharmProjects\contextis'
    csv_filepath = r'mid-level-interview-master\data\logins.csv'
    db_filepath = r'mid-level-interview-master\data\database.sqlite'
    servers = defaultdict(set)
    user_names = defaultdict(Counter)
    user_emails = defaultdict(set)
    user_phones = defaultdict(set)
    logins = set()

    connection = sqlite3.connect(path.join(root, db_filepath))
    cursor = connection.cursor()

    with open(path.join(root, csv_filepath), 'r', encoding='UTF-8') as infile:
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
            logins.add((user, ip, decode_login(login)))
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

if __name__ == '__main__':
    main()
