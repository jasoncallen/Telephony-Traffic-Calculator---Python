""" Telephony Traffic Calculator - Python.

Traffic Tool to calculate Erlang, Erlang B (Channel requirement and Blocking
Probability) and Network Bandwidth for VoIP solutions.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Jason Callen"
__credits__ = ["Jason Callen"]
__license__ = "GPLv3"
__version__ = "1.0.1"
__maintainer__ = "Jason Callen"
__email__ = "jason@jasoncallenenterprises.com"
__status__ = "Production"
__date__ = "2022/08/10"
__deprecated__ = False

import os
import textwrap

###############################################################################
# -----------------------Defined Prompts---------------------------------------
###############################################################################

traffic_main_menu = '''Traffic Calculations\n
1: Erlang - calculate load of traffic
2: Erlang B - calculate number of channels
3: Erlang B Blocking Probability - calculate chance to block calls
4: Network Bandwidth - calculate bandwidth for given codec and call count\n\n
Press Q to return to main menu'''

codec_prompt = '''Codec Selection\n
1: G.711 (20ms)
2: G.723.1 (5.3 Kbps) (30ms)
3: G.723.1 (6.3 Kbps) (30ms)
4: G.726 (24 Kbps) (20ms)
5: G.726 (32 Kbps) (20ms)
6: G.728 (30ms)
7: G.729 (20ms)
8: G722 (20ms)\n
Which Codec would you like to use: '''

network_layer_prompt = '''Network Layers\n
1: Network (L1) - most
2: Channel (L2)
3: IP
4: UDP
5: RTP
6: Data - least\n
What layer of Network do you want to calculate from: '''

vlan_tag_prompt = '''802.1Q
1: Yes
2: No

Do you want to include in calculation: '''

silence_prompt = "Because Silence Suppression (or Voice Activity Detection) can vary widely in bandwidth reduction, it was not taken into consideration. For purposes of planning and design, Silence Suppression should never be used for circuits less than 24 concurrent calls. Also keep in mind things like music on hold render it useless as well."

###############################################################################################
# ---------------------------Defined Functions-------------------------------------------------
###############################################################################################


def menu_check_min_max(prompt, min_value, max_value):
    # Function to check input int with a max value
    while (True):
        option = ''
        try:
            option = input(prompt)
            if option.upper() == 'Q':
                return option.upper()
            if int(option) >= min_value and int(option) <= max_value:
                return int(option)
            else:
                print('Invalid option. Please enter a number between', min_value, ' and', max_value)
        except ValueError:
            if not option:
                print('Entry cannot be empty.')
            else:
                print('Invalid option. Please enter a number between', min_value, ' and', max_value)
        except KeyboardInterrupt:
            print('\nPlease do not stop the program.')


def menu_check_no_max_int(prompt):
    # Function to check input int without a max value
    while (True):
        try:
            option = input(prompt)
            if int(option) > 0:
                return int(option)
            else:
                print('Invalid option. Must be a whole number greater than 0')
        except ValueError:
            if not option:
                print('Entry cannot be empty.')
            else:
                print('Invalid option. Please enter a whole number.')
        except KeyboardInterrupt:
            print('\nPlease do not stop the program.')


def menu_check_no_max_float(prompt):
    # Function to check input float without a max value
    while (True):
        option = ''
        try:
            option = input(prompt)
            if float(option) > 0:
                return float(option)
            else:
                print('Invalid option. Number must be greater than 0')
        except ValueError:
            if not option:
                print('Entry cannot be empty.')
            else:
                print('Invalid option. Please enter a number.')
        except KeyboardInterrupt:
            print('\nPlease do not stop the program.')


def pause_clear():
    # Function will pause and clear the screen
    os.system('pause')
    os.system('cls')


def traffic_menu():
    # Function to start traffic menu
    while (True):
        print(traffic_main_menu)
        option = menu_check_min_max('\nEnter a number: ', 1, 4)
        if option == 'Q':
            return
        if option == 1:
            os.system('cls')
            traffic_menu_item_1()
            pause_clear()
        elif option == 2:
            os.system('cls')
            traffic_menu_item_2()
            pause_clear()
        elif option == 3:
            os.system('cls')
            traffic_menu_item_3()
            pause_clear()
        elif option == 4:
            os.system('cls')
            traffic_menu_item_4()
            pause_clear()


def traffic_menu_item_1():
    # Function to calculate the erlang value for call rate, handle and hold time.
    arrival_rate = menu_check_no_max_int('Enter the number of calls per minute: ')
    mean_hold_time = menu_check_no_max_int('Enter the Mean Hold time in seconds: ')
    average_call_time = menu_check_no_max_int('Enter the Average Call Time in seconds: ')
    total_time = (mean_hold_time + average_call_time) / 60
    erlangs = "{:.03f}".format(round((arrival_rate * total_time) / 60, 4))

    print('\n\nTotal traffic Erlangs offered in an hour is', erlangs, '\n\n')


def traffic_menu_item_2():
    # Function to calculate the required channels for the given traffic load and block percentage
    channel = 1
    previous_d = 1
    previous_e = 1

    erlangs = menu_check_no_max_float('Enter amount of Erlang per hour: ')
    block_level_goal = menu_check_no_max_float('Enter the block level. i.e .03 is 3 calls out of 100: ')
    while (True):
        block_percentage = ((erlangs / channel) * previous_d) / (previous_e + ((erlangs / channel) * previous_d))
        previous_e = previous_e + ((erlangs / channel) * previous_d)
        previous_d = (erlangs / channel) * previous_d
        if block_percentage < block_level_goal:
            break
        channel += 1
    print('\n\nYou would require', channel, 'channels.\n\n')


def traffic_menu_item_3():
    # Function to get values from user and calculate block.
    erlangs = menu_check_no_max_float('Enter amount of Erlang per hour: ')
    channels = menu_check_no_max_int('Number of channels: ')
    grade_of_service = traffic_probability_block(erlangs, channels)
    print('\n\nThere would be a', grade_of_service, ' chance to block calls.\n\n')


def traffic_menu_item_4():
    # Function to calculate the estimated bandwidth requirement for a given codec
    number_of_calls = menu_check_no_max_int('Enter number of concurrent calls: ')
    os.system('cls')
    codec_sample_size_input = menu_check_min_max(codec_prompt, 1, 8)
    packets_per_second_tuple = (0, 50, 33.333, 33.333, 50, 50, 33.333, 50, 50)
    codec_sample_size_tuple = (0, 160, 20, 24, 60, 80, 60, 20, 160)
    os.system('cls')
    packets_per_second = packets_per_second_tuple[codec_sample_size_input]
    codec_sample_size = codec_sample_size_tuple[codec_sample_size_input]
    os.system('cls')
    protocol_stack_size_input = menu_check_min_max(network_layer_prompt, 1, 6)
    packet_size_tuple = (0, 78, 58, 40, 20, 8, 0)
    os.system('cls')
    protocol_stack_size = packet_size_tuple[protocol_stack_size_input]
    os.system('cls')
    if menu_check_min_max(vlan_tag_prompt, 1, 2) == 1:
        vlan_tag_size = 4
    else:
        vlan_tag_size = 0
    os.system('cls')
    voip_data_size = codec_sample_size * 1
    total_packets_per_second = packets_per_second * number_of_calls
    kbps_answer = "{:,}".format(round((voip_data_size + protocol_stack_size + vlan_tag_size) * total_packets_per_second * 8 / 1000, 2))
    wrapped_lines = textwrap.wrap(silence_prompt)
    print("\n".join(wrapped_lines))
    print('\n\nIt will require approximately', kbps_answer, 'Kbps.\n\n')


def traffic_probability_block(offer, channels):
    # Function to calculate block probability
    b = 1
    k = 1
    count = 0
    while k <= channels:

        count += 1
        b = 1+(count*b)/offer
        k += 1
    block_probability = 1/b
    percentage = "{:.02%}".format(block_probability)
    return percentage


if __name__ == "__main__":
    traffic_menu()
