from os.path import isfile
from sqlite3 import connect

from apscheduler.triggers.cron import CronTrigger

# Create/find .sql and .db files
DB_PATH = "./data/db/userlevels.db"
BUILD_PATH = "./data/db/build.sql"

connection = connect(DB_PATH, check_same_thread=False)
cursor = connection.cursor()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner


@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)


def autosave(scheduler):
    scheduler.add_job(commit, CronTrigger(second=0))


def commit():
    connection.commit()


def close():
    connection.close()


def field(command, *values):
    cursor.execute(command, tuple(values))

    if (fetch := cursor.fetchone()) is not None:
        return fetch[0]


def record(command, *values):
    cursor.execute(command, tuple(values))
    return cursor.fetchone()


def records(command, *values):
    cursor.execute(command, tuple(values))
    return cursor.fetchall()


def column(command, *values):
    cursor.execute(command, tuple(values))
    return [item[0] for item in cursor.fetchall()]


def execute(command, *values):
    cursor.execute(command, tuple(values))


def multiexecute(command, valueset):
    cursor.executemany(command, valueset)


def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cursor.executescript(script.read())
