DROP TABLE IF EXISTS item_comment_revision;
DROP TABLE IF EXISTS item_comment;
DROP TABLE IF EXISTS item_tag_junction;
DROP TABLE IF EXISTS item_tag;
DROP TABLE IF EXISTS item_revision;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash CHAR(97) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    password_reset_required BOOLEAN NOT NULL
);

CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(256) NOT NULL UNIQUE,
    description VARCHAR(1024),
    quantity INTEGER NOT NULL DEFAULT 0,
    unit VARCHAR(100)
);

CREATE TABLE item_revision (
    _id INTEGER PRIMARY KEY AUTO_INCREMENT,
    _user_id INTEGER,
    _datetime DATETIME,
    id INTEGER NOT NULL,
    name VARCHAR(256),
    description VARCHAR(1024),
    quantity INTEGER NOT NULL,
    unit VARCHAR(100),
    FOREIGN KEY (id) REFERENCES item(id) ON DELETE CASCADE
);

CREATE TABLE item_comment (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER,
    item_id INTEGER NOT NULL,
    text VARCHAR(2000) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE
);

CREATE TABLE item_comment_revision (
    _id INTEGER PRIMARY KEY AUTO_INCREMENT,
    _user_id INTEGER,
    _datetime DATETIME,
    id INTEGER NOT NULL,
    text VARCHAR(2000) NOT NULL,
    FOREIGN KEY (id) REFERENCES item_comment(id) ON DELETE CASCADE
);

CREATE TABLE item_tag (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE item_tag_junction (
    item_id INTEGER,
    item_tag_id INTEGER,
    PRIMARY KEY (item_id, item_tag_id),
    FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE,
    FOREIGN KEY (item_tag_id) REFERENCES item_tag(id) ON DELETE CASCADE
);
