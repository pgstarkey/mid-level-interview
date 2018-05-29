"""
Module to import CSV file in isolation
"""

from collections import Counter, defaultdict
import csv
from datetime import datetime
from itertools import permutations
from os import path
import re

email = re.compile(r'[\w.-]+@[\w.-]+\.\w+')
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
    filepath = r'mid-level-interview-master\data\logins.csv'
    servers = defaultdict(set)
    user_names = defaultdict(Counter)
    user_emails = defaultdict(set)
    user_phones = defaultdict(set)
    server_logins = defaultdict(set)

    with open(path.join(root, filepath), 'r', encoding='UTF-8') as infile:
        csv_reader = csv.reader(infile)
        next(csv_reader)
        for (server, ip, user, username, contact, login) in csv_reader:
            if valid_ip(ip):
                servers[ip].add(server)
            user_names[user].update([username])
            if email.match(contact):
                user_emails[user].add(contact)
            else:
                user_phones[user].add(phone_number(contact))
            server_logins[ip].add((user, decode_login(login)))
    for ip in servers:
        print(ip, servers[ip])

    for user in user_names:
        print(user, user_names[user].most_common(1)[0][0])
        print(user, user_emails[user], user_phones[user])
    for ip in server_logins:
        for user, login in server_logins[ip]:
            print(ip, user, login)


if __name__ == '__main__':
    main()
