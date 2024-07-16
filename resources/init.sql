DROP TABLE IF EXISTS new_issue;
DROP TABLE IF EXISTS current_issue;
DROP TABLE IF EXISTS state;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id DECIMAL NOT NULL PRIMARY KEY,
    jira_username VARCHAR,
    is_manager BOOLEAN
)

CREATE TABLE state (
    user_id DECIMAL PRIMARY KEY,
    state INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE current_issue (
    user_id DECIMAL PRIMARY KEY,
    issue_key VARCHAR NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE new_issue (
    user_id DECIMAL PRIMARY KEY,
    project VARCHAR,
    summary VARCHAR,
    assignee VARCHAR,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
