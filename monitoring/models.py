from django.db import models


class Servers(models.Model):
    ip = models.TextField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'servers'


class Users(models.Model):
    user = models.TextField(primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'users'


class UserEmails(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, db_column='user',
                             primary_key=True)
    email = models.TextField()

    class Meta:
        managed = False
        db_table = 'user_emails'
        unique_together = (('user', 'email'),)


class UserPhones(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, db_column='user',
                             primary_key=True)
    phone = models.TextField()

    class Meta:
        managed = False
        db_table = 'user_phones'
        unique_together = (('user', 'phone'),)


class Logins(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, db_column='user',
                             primary_key=True)
    server = models.ForeignKey('Servers', models.DO_NOTHING, db_column='server')
    datetime = models.TextField()
    class Meta:
        managed = False
        db_table = 'logins'
        unique_together = (('user', 'server', 'datetime'),)
