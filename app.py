#import libraries and modules
import database
from typing import List
from connections.connection_pool import get_connection
from models.options import Option
from models.polls import Poll
import random
import charts
import matplotlib.pyplot as plt
import platform

MENU_PROMPT = """\n\n------ Menu ------

1) Create new poll
2) List open polls
3) Vote on a poll
4) Show poll votes
5) Select a random winner from a poll option
6) Create pie chart for plot results
7) Exit

Enter your choice: \n"""

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
    print("\n\t\t------Open Polls------\n\n")
    for poll in polls:
        print(f"\t\t{poll.id}: {poll.title} (created by {poll.owner})")


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

def poll_name_by_id(polls, poll_id):
    for poll in polls:
        if poll.id == poll_id:
            return poll.title
    return "No title"


def randomize_poll_winner():
    poll_id = int(input("Enter poll you'd like to pick a winner for: "))

    options = Poll.get(poll_id).options
    _print_poll_options(options)

    option_id = int(input("Enter which is the winning option, we'll pick a random winner from voters: "))
    votes = Option.get(option_id).votes    
    winner = random.choice(votes)
    print(f"The randomly selected winner is {winner[0]}.")

def save_plot(options, votes, poll_name):
    # prompt for desire to save plot
    save_plot = input("Press 'y' to save this plot (press any other key to go back to main menu): ")

    # save plot
    if save_plot.lower() == 'y':
        # create figure again as plt.show() destroys figure
        fig = charts.create_pie_chart(options, votes, poll_name)
        # modify poll name in order to delete special characters
        for char in ['?','*', '.', '"',"'", '/', '[', ']', ':', ';', '|']:
            poll_name = poll_name.replace(char, "").strip()
        # check OS (in order to use correct slash for saving)
        current_os = platform.system()
        # save figure with path adjusted to OS
        if current_os == 'Windows':
            plt.savefig(f"saved_plots\{poll_name}.png", dpi=400, bbox_inches='tight') 
        elif (current_os == 'Linux') or (current_os == 'Darwin') :
            plt.savefig(f"saved_plots/{poll_name}.png", dpi=400, bbox_inches='tight') 
        print(f"Plot successfully saved as '{poll_name}.png' in the following directory: 'saved_plots'")
        plt.close('all') #destroy figure

def create_plt_fig():
    # print all polls and IDs as guide
    polls = Poll.all()
    print("\n\t\t------Available Polls------\n\n")
    for poll in polls:
        print(f"\t\t{poll.id}: {poll.title} (created by {poll.owner})")

    # select poll of interest
    poll_id = int(input("Enter poll you'd like to see a figure for: "))
    

    # save poll name of selected poll to variable (to pass to create_pie_chart() )
    poll_name = poll_name_by_id(polls, poll_id)

    # get vote info for selected poll
    options, votes = Poll.get_info_for_plt(poll_id) 

    # create figure
    fig = charts.create_pie_chart(options, votes, poll_name)
    plt.show()

    save_plot(options, votes, poll_name)



MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomize_poll_winner,
    "6": create_plt_fig
}


def menu():
    with get_connection() as connection:
        database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != "7":
        try:
            MENU_OPTIONS[selection]()
        except KeyError:
            print("Invalid input selected. Please try again.")


menu()