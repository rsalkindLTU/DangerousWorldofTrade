'''
This file contains function wrappers for console input
and output. Depending on the function, this file may
use Pyperclip to put information onto the user's
clipboard.

Requires: pyperclip (>=1.7.0)
'''
from file_finder import find_journal_directory
import pyperclip as pc
import random
from os.path import dirname

def startup_info():
    '''
    This function will be used for user input for some things
    that we need to know about the player.
    '''
    # First, greet the user and ask them for the commander name.
    greeting = '''Greetings commander! It looks like you have not set up this program before.
    For this to work, I'm going to need a few things from you.'''

    print(greeting)
    commander_name = input("First of all, what do you want to be called? ")

    g2 = f'''Okay {commander_name}, a few more things before setup is complete.'''

    print(g2)
    ship_range = input("What is the max jump range of your ship fully laden? ")

    cargo_size = input("Okay, what is the size of your cargo hold? ")

    print("One last thing. You're going to get prompted for the location of your journal files.")
    print("Find those for me and we'll continue.")

    journal_path = find_journal_directory()

    print("Okay, that's all we need. Running the program. . .")

    return (commander_name, ship_range, dirname(journal_path), cargo_size)

def next_location_to_buy(future):
    '''
    This function is called once a future looking for
    the next place to go returns. It will output
    the text information to the user and will copy the
    system to the clipboard for the user.

    The future.result() will be formatted like:
        (system, station, product, quantity)
    The system and station are the next location,
    the product and quantity are what to buy before leaving
    '''
    #print(future.result())
    greetings = [
        "===> Okay commander. You will be traveling to {} in the {} system.",
        "===> The results are in: time to set course for {}, in the {} system.",
        "===> Hey commander, computer is sayin' you need to head for {}, somewhere in the {} system next.",
        "===> Head towards {}, {}. Not too much of a long haul, right?",
        "===> Forecast says slightly cloudy with a chance of piracy at {}, {}. Start heading that direction."
    ]
    purchases = [
        "===> You should buy {} -- about {} tons of it -- if you want to make a profit there.",
        "===> Survey also says 'buy {}'. Dunno why it wants you to grab {} tons of them, but profit's profit.",
        "===> I got a good feeling about {}. Buy {} tons before you go.",
        "===> Looks like {} are pretty hot right now. See if taking {} of them will get you far.",
        "===> You'll be a beacon for pirates with {}. Especially with {} tons of it."
    ]

    # Determine the greeting and pruchase text
    greeting = random.sample(greetings, 1)
    purchase = random.sample(purchases, 1)

    # Get the result out of the future
    system, station, product, quantity = future.result()

    # Write where the player will be going
    print(greeting[0].format(station, system))
    print(purchase[0].format(product, quantity))
    print("The location has been copied to your clipboard.")

    # Copy the system to the clipboard
    pc.copy(system)


