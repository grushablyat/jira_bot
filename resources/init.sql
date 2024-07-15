DROP TABLE IF EXISTS new_issue;
DROP TABLE IF EXISTS current_issue;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
--     id SERIAL PRIMARY KEY,
    id DECIMAL NOT NULL PRIMARY KEY,
    state INT
);

CREATE TABLE current_issue (
    user_id DECIMAL PRIMARY KEY,
    issue VARCHAR NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE new_issue (
    user_id DECIMAL PRIMARY KEY,
    project VARCHAR(255),
    title VARCHAR(255),
    assignee VARCHAR(255),
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
