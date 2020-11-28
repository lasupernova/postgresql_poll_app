#import libraries and modules
import database
from typing import List
from connections.connection_pool import get_connection
from models.options import Option
from models.polls import Poll
import random

DATABASE_PROMPT = "Enter the DATABASE_URI value or leave empty to load from .env file: "
MENU_PROMPT = """-- Menu --

1) Create new poll
2) List open polls
3) Vote on a poll
4) Show poll votes
5) Select a random winner from a poll option
6) Exit

Enter your choice: """

NEW_OPTION_PROMPT = "Enter new option text (or leave empty to stop adding options): "


def prompt_create_poll():
    poll_title = input("Enter poll title: ")
    poll_owner = input("Enter poll owner: ")
    poll = Poll(poll_title, poll_owner)
    poll.save()

    while (new_option := input(NEW_OPTION_PROMPT)):
        poll.add_option(new_option)

def list_open_polls():
    polls = Poll.all()

    for poll in polls:
        print(f"{poll.id}: {poll.title} (created by {poll.owner})")


def prompt_vote_poll():
    poll_id = int(input("Enter poll would you like to vote on: "))
    poll = Poll.get(poll_id)
    options = poll.options
    _print_poll_options(options)

    option_id = int(input("Enter option you'd like to vote for: "))
    username = input("Enter the username you'd like to vote as: ")
    
    Option.get(option_id).vote(username)


def _print_poll_options(options: List[Option]):
    for option in options:
        print(f"{option.id}: {option.text}")


def show_poll_votes():
    # get input on which poll's info to see
    poll_id = int(input("Enter poll you would like to see votes for: "))

    # get poll of interest
    poll = Poll.get(poll_id)
    # get options for that poll
    options = poll.options
    # get number of votes per option
    votes_per_option = [len(option.votes) for option in options]
    # calculate the total number of votes from values in list
    total_votes = sum(votes_per_option)

    # iterate over options and according votes and print out info
    try:
        for option, votes in zip(options, votes_per_option):
            percentage = votes/total_votes * 100
            print(f"{option.text}: got {votes} votes ({percentage}% of total votes)")
    except ZeroDivisionError:
        print("No votes were casted for this poll yet.")


def randomize_poll_winner():
    poll_id = int(input("Enter poll you'd like to pick a winner for: "))

    options = Poll.get(poll_id).options
    _print_poll_options(options)

    option_id = int(input("Enter which is the winning option, we'll pick a random winner from voters: "))
    votes = Option.get(option_id).votes    
    winner = random.choice(votes)
    print(f"The randomly selected winner is {winner[0]}.")


MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomize_poll_winner
}


def menu():
    with get_connection() as connection:
        database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != "6":
        try:
            MENU_OPTIONS[selection]()
        except KeyError:
            print("Invalid input selected. Please try again.")


menu()