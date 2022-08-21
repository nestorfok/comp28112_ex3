#!/usr/bin/python3

import reservationapi
import configparser
import random

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the hotel API
hotel = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

# Your code goes here

# Check if we hold 2 reservations on system (3.4)
print("Getting slot held")
x = hotel.get_slots_held()
slot_held = []
for i in x:
    slot_held.append(int(i['id']))
print("The slot held is ", slot_held)

# Release slot if there is more than 2 slot (3.2)
if len(slot_held) >= 2:
    slot_release = random.choice(slot_held)
    print("Releasing slot %d" % slot_release)
    x = hotel.release_slot(slot_release)
    print(x['message'])
    slot_held.remove(slot_release)

# Get the slot available (3.3)
print("Getting slot available")
x = hotel.get_slots_available()
slot_available = []
for i in x:
    slot_available.append(int(i['id']))
print("The slots available is\n", slot_available)

# Book a random slot (3.1)
slot_book = random.choice(slot_available)
print("Booking slot %d" % slot_book)
x = hotel.reserve_slot(slot_book)
slot_held.append(int(x['id']))
print("Booked slot %d" % int(x['id']))

# Release a random slot (3.2)
slot_release = random.choice(slot_held)
print("Releasing slot %d" % slot_release)
x = hotel.release_slot(slot_release)
print(x['message'])







