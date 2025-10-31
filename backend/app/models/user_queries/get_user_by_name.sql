SELECT id, username, password_hash, created_at, last_login, password_reset_required FROM user
WHERE username = %s;
