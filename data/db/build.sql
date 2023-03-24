CREATE TABLE IF NOT EXISTS exp (
	UserId integer PRIMARY KEY,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS warnlog (
	UserId integer,
	Reason text
);
CREATE TABLE IF NOT EXISTS robloxverification (
	UserId integer PRIMARY KEY,
	RobloxProfileLink text DEFAULT ""
);
CREATE TABLE IF NOT EXISTS oauth (
    UserId INTEGER PRIMARY KEY,
    Token text DEFAULT "",
	Expires integer DEFAULT 0,
	RefreshToken text DEFAULT "",
	Scope text DEFAULT "",
	TokenType text DEFAULT ""
);