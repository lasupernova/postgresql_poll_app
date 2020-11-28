# import libraries
from psycopg2.extras import execute_values #used to avoid for-loop to add multiple entries
from typing import List, Tuple #for type-hinting

# create custom types to pass for type hinting
Poll = Tuple[int, str, str] #the 'Poll'-type is a tuple with an integer, followed by 2 strings as values
Vote = Tuple[str, int]
Option = Tuple[int, str, int]
# PollResults = Tuple[int, str, int, float] #as poll results will include [poll_id, option_value, option_count, option_percentage] --> not used anymore

CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls
(id SERIAL PRIMARY KEY, title TEXT, owner_username TEXT);"""
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options
(id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER, FOREIGN KEY (poll_id) REFERENCES polls(id));"""
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes
(username TEXT, option_id INTEGER, FOREIGN KEY (option_id) REFERENCES options(id));"""

SELECT_POLL = """SELECT * FROM polls WHERE id=%s;"""
SELECT_ALL_POLLS = "SELECT * FROM polls;"
SELECT_POLL_OPTIONS = """SELECT * FROM options WHERE poll_id = %s;"""
SELECT_LATEST_POLL = """SELECT * FROM polls
                        WHERE polls.id = (
                            SELECT id FROM polls ORDER_BY id DESC LIMIT 1
                        );
                        """
INSERT_OPTION_RETURN_ID = "INSERT INTO options (option_text, poll_id) VALUES (%s, %s) RETURNING id;" #only one "%s", as tuple is goinf to be passed (tuple: (option_entry, poll_id) )
INSERT_VOTE = "INSERT INTO votes (username, option_id) VALUES (%s, %s);"
SELECT_OPTION = """SELECT * FROM options WHERE id=%s;"""
SELECT_VOTES_FOR_OPTION = """SELECT * FROM votes WHERE option_id=%s;"""
SELECT_OPTIONS_IN_POLL_FOR_PLT = """
                                 SELECT options.option_text, COUNT(votes.option_id) FROM options
                                 JOIN polls ON options.poll_id = polls.id
                                 JOIN votes on options.id = votes.option_id
                                 WHERE polls.id = %s
                                 GROUP BY (options.option_text, votes.option_id);
                                """

def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_POLLS)
            cursor.execute(CREATE_OPTIONS)
            cursor.execute(CREATE_VOTES)

""" Poll Functions """

def create_poll(connection, title: str, owner: str):
    query_poll = """INSERT INTO polls (title, owner_username) VALUES (%s, %s) RETURNING id;""" #returns id after insertion
    with connection:
        with connection.cursor() as cursor:
            # insert poll into polls-table
            cursor.execute(query_poll, (title, owner))
            # get poll_id of inserted poll (done by use of RETURNING; to pass id to option-table in next step) and save in tuple with options
            p_id = cursor.fetchone()[0]
            return p_id  

def get_poll(connection, poll_id: int) -> Poll:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL, (poll_id, ))
            return cursor.fetchone()

def get_polls(connection) -> List[Poll]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_POLLS)
            return cursor.fetchall()


def get_latest_poll(connection) -> Poll:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_LATEST_POLL)
            return cursor.fetchone()


def get_poll_options(connection, poll_id: int) -> List[Option]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
            return cursor.fetchall()

def get_poll_options_for_plt(connection, poll_id: int) -> List[Option]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_OPTIONS_IN_POLL_FOR_PLT, (poll_id,))
            return cursor.fetchall()

"""Functions for Options"""

def get_option(connection, option_id: int) -> Option:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_OPTION, (option_id, ))
            return cursor.fetchone()

def add_option(connection, option_text: str, poll_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_OPTION_RETURN_ID, (option_text, poll_id))  
            option_id = cursor.fetchone()[0]
            return option_id


"""Functions for Votes"""

def get_votes_for_option(connection, option_id: int) -> List[Vote]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_VOTES_FOR_OPTION, (option_id, ))  
            return cursor.fetchall()

def add_poll_vote(connection, username: str, option_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_VOTE, (username, option_id))