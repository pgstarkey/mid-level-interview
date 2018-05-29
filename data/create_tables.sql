CREATE TABLE servers (
  ip text PRIMARY KEY,
  name text NOT NULL
  );

CREATE TABLE users (
  user text PRIMARY KEY,
  name text NOT NULL
  );

CREATE TABLE logins (
  user text NOT NULL,
  server text NOT NULL,
  datetime text NOT NULL,
  PRIMARY KEY (user, server, datetime),
  FOREIGN KEY (user) REFERENCES users(user),
  FOREIGN KEY (server) REFERENCES servers(ip)
  );

CREATE TABLE user_emails (
  user text NOT NULL,
  email text NOT NULL,
  PRIMARY KEY (user, email),
  FOREIGN KEY (user) REFERENCES users(user)
  );

CREATE TABLE user_phones (
  user text NOT NULL,
  phone text NOT NULL,
  PRIMARY KEY (user, phone),
  FOREIGN KEY (user) REFERENCES users(user)
  );
