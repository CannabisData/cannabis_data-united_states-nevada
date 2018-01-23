"""Script to geocode Nevada licensee data."""

import os
import json
import sys
import time
from geopy import geocoders
from geopy.geocoders import GoogleV3

SOURCE_FILENAME = 'nevada-licensees-05-clean.json'
TARGET_FILENAME = 'nevada-licensees-10-geocoded.json'
PLACE_ID = 'place_id'
LAT = 'latitude'
LNG = 'longitude'
GEO = 'geo'

# If the TARGET_FILENAME exists, pull in interim results
if os.path.isfile(TARGET_FILENAME):
    SOURCE_FILENAME = TARGET_FILENAME


def main():
    """Main program."""
    licensees = []
    print('Reading input from {}'.format(SOURCE_FILENAME))
    with open(SOURCE_FILENAME, 'r') as infile:
        licensees = json.load(infile)

    total_licensees = len(licensees)
    print('Total licensee records: {}'.format(total_licensees))

    print('Geocoding licensees...')

    # Retrieve the Google Maps API key and create a geocoder
    api_key = os.getenv('GOOGLE_MAPS')
    google_maps = GoogleV3(api_key=api_key)
    print('* Using Google Maps geocoder...')
    print("  + API Key: '{}'".format(api_key))

    geocodes = {}
    prior = 0
    geocoded = 0
    duplicates = 0
    for licensee in licensees:
        try:
            address = licensee['Loc City'] + ', Nevada'

            # Dispensaries are listed with an exact address
            if 'Loc Addr' in licensee:
                address = licensee['Loc Addr'] + ', ' + address

            print('* Address: {}'.format(address))

            if address in geocodes:
                licensee[LAT] = geocodes[address][LAT]
                licensee[LNG] = geocodes[address][LNG]
                duplicates += 1
                print('  - Geocoded this session ({})'.format(duplicates))
                continue

            if GEO in licensee:
                prior += 1
                geocodes[address] = {LAT: licensee[LAT], LNG: licensee[LNG]}
                print('  - Geocoded prior ({}): {}'.format(prior,
                                                           geocodes[address]))
                continue

            print('  + Geocoding...')
            location = google_maps.geocode(address, timeout=15)
            geocoded += 1
            licensee[LAT] = location.latitude
            licensee[LNG] = location.longitude
            licensee[GEO] = location.raw
            geocodes[address] = {LAT: licensee[LAT], LNG: licensee[LNG]}

            print('  + {}, {}'.format(licensee[LAT], licensee[LNG]))
#            print('  + Raw: {}'.format(licensee[GEO]))
        except:
            print('Unexpected error: ', sys.exc_info()[0])

        # Courtesy pause
        time.sleep(1)
#        break

    print('Writing output to {}'.format(TARGET_FILENAME))
    with open(TARGET_FILENAME, 'w') as outfile:
        json.dump(licensees, outfile, sort_keys=True, indent=2,
                  separators=(',', ': '))

    print('Summary')
    print('  + Prior: {}'.format(prior))
    print('  + Gecoded: {}'.format(geocoded))
    print('  + Duplicates: {}'.format(duplicates))
    remaining = total_licensees - prior - geocoded - duplicates
    print('  - Remaining: {}'.format(remaining))


main()
