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

# Create an API object to communicate with the band API
band = reservationapi.ReservationApi(config['band']['url'],
                                       config['band']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

correct = 0
while correct < 5:

    # Initialise 2 list to store the available slot of hotel and band
    slot_free_hotel = []
    slot_free_band = []

    # Request available free slot from hotel and band
    print("Getting free slots available from hotel and band")
    x = hotel.get_slots_available()
    y = band.get_slots_available()

    # Turn the free slot in a list
    for i in x:
        slot_free_hotel.append(int(i['id']))
    for j in y:
        slot_free_band.append(int(j['id']))
    print("Successfully get free slots available from hotel and band")

    # Loop again if no slot is available
    if len(slot_free_band) == 0 or len(slot_free_hotel) == 0:
        continue

    # Get the earliest free slot for both of them
    earliest_slot = -1
    for i in slot_free_hotel:
        if i in slot_free_band:
            earliest_slot = i
            break

    # Get the slot held by hotel and band
    print("Getting slot held by hotel and band")
    x = hotel.get_slots_held()
    y = band.get_slots_held()
    slot_held_hotel = []
    slot_held_band = []
    for i in x:
        slot_held_hotel.append(int(i['id']))
    for j in y:
        slot_held_band.append(int(j['id']))
    print("The slot held by hotel is ", slot_held_hotel)
    print("The slot held by band is ", slot_held_band)

    # Get the real earliest slot
    if len(slot_held_hotel) == 0 and len(slot_held_band) == 0:
        pass
    else:
        # hotel has booked the earliest slot and it is a free slot in band
        if len(slot_held_hotel) > 0 and slot_held_hotel[0] < earliest_slot and slot_held_hotel[0] in slot_free_band:
            earliest_slot = slot_held_hotel[0]
        # band has booked the earliest slot and it is a free slot in hotel
        elif len(slot_held_band) > 0 and slot_held_band[0] < earliest_slot and slot_held_band[0] in slot_free_hotel:
            earliest_slot = slot_held_band[0]
        # both hotel and band has booked the earliest slot
        elif len(slot_held_band) > 0 and len(slot_held_hotel) > 0:
            if slot_held_band[0] < earliest_slot and slot_held_band[0] in slot_held_hotel:
                earliest_slot = slot_held_band[0]
            elif slot_held_hotel[0] < earliest_slot and slot_held_hotel[0] in slot_held_band:
                earliest_slot = slot_held_hotel[0]

    # Loop again if no common slot
    if earliest_slot == -1:
        continue

    print("The earliest slot is ", earliest_slot)

    # Book the earliest slot for hotel and band
    print("Booking slot...")
    correct1 = 0
    correct2 = 0
    if earliest_slot not in slot_held_hotel:
        try:
            x = hotel.reserve_slot(earliest_slot)
            print("booked hotel slot %d" % earliest_slot)
            correct1 = 1
        except:
            earliest_slot = -1
            print("cannot book hotel slot %d" % earliest_slot)
    else:
        x = {'id': earliest_slot}
        print("booked hotel slot %d" % earliest_slot)
        correct1 = 1

    if earliest_slot not in slot_held_band:
        try:
            y = band.reserve_slot(earliest_slot)
            print("booked band slot %d" % earliest_slot)
            correct2 = 1
        except:
            earliest_slot = -1
            print("cannot book band slot %d" % earliest_slot)
    else:
        y = {'id': earliest_slot}
        print("booked band slot %d" % earliest_slot)
        correct2 = 1

    if correct1 == 1 and correct2 == 1:
        correct += 1

    else:
        # Check if there both hotel and band already hold the same slot
        for i in slot_held_hotel:
            if i in slot_held_band:
                earliest_slot = i

    # Remove extra slots
    for i in slot_held_hotel:
        if i != earliest_slot:
            print("Releasing slot %d" % i)
            x = hotel.release_slot(i)
            print(x['message'])

    for j in slot_held_band:
        if j != earliest_slot:
            print("Releasing slot %d" % j)
            y = band.release_slot(j)
            print(y['message'])


