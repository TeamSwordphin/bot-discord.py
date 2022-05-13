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