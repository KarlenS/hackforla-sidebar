from collections import OrderedDict
import pandas as pd
import operator
from ast import literal_eval
import time
import json

import matplotlib.pyplot as plt

guest_host_field_assoc = {
    'number_of_guests':'hosting_amount',
    'guests_relationship':'youth_relationship',
    'parenting_guest':'youth_parenting',
    'pets_have':'pets_hosting',
    'host_pet_restrictions':'pets_list',
    'duration_of_stay':'duration_of_stay',
    'smoking_household_acceptable':'smoking_allowed',
    'drinking_household_acceptable':'drinking_residents',
    'substances_household_acceptable':'substances_residents'
}


def count_matches(filename = 'matches.json',
                  dynamic_bins = True,
                  plot = True):

    data = read_json_file(filename)

    guest_counts = {}
    host_counts = {}

    for entry in data:
        if entry['guestId'] not in guest_counts.keys():
            guest_counts[entry['guestId']] = 0
        if entry['hostId'] not in host_counts.keys():
            host_counts[entry['hostId']] = 0


        if not entry['restrictionsFailed']:
            guest_counts[entry['guestId']] = guest_counts[entry['guestId']] + 1
            host_counts[entry['hostId']] = host_counts[entry['hostId']] + 1

    if dynamic_bins:
        plt.hist(guest_counts.values(),bins=2*max(guest_counts.values()))
    else:
        plt.hist(guest_counts.values(),bins=10)

    plt.xlabel('# of matched hosts')
    plt.ylabel('# of guests')
    plt.show()

    return guest_counts,host_counts

def read_file(filename, converters = None):

    return pd.read_csv(filename, converters=converters)

def read_json_file(filename):

    with open(filename) as f:
        data = json.load(f)

    return data


def categorical_filter(guest, host, allcat = True, reverse=False):
    '''
    returns False for passed filter, true for failed

    expects lists for both guest and host
    default (reverse = False) will check if any in guest
    are in host; reverse = True will check if all in guest are in host
    '''


    if allcat:
        #all in guest are in host
        match = not set(guest).issubset(set(host))
        #return set(guest) & set(host)
    else:
        #any in guest are in host
        match = not (set(guest) & set(host))

    if reverse:
        return not match
    else:
        return match


def generic_filter(guest, host, op):
    '''
    False meansfilter is passed, true means constraint is failed
    '''
    return op(guest, host)


def bool_filter(guest,host,reverse=False):
    '''
    e.g., reverse=False: indoor_smoking_ok & indoor_smoking
            1 0 = false
            1 1 = false
            0 1 = true
            0 0 = false
          reverse=True: guest_is_parent & guest_is_parent
          1 0 = true
          1 1 = false
          0 1 = false
          0 0 = false

    '''

    if reverse:
        return guest and not host
    else:
        return not guest and host


def filter_pair(guest, host):
    '''
    this could be sooo much better
    '''

    # categorical_match = [('pets_list',True,False),
    #                      ('host_pet_restrictions',False,True),
    #                      ('duration_of_stay',False,False)]
    categorical_match = [('duration_of_stay',False,False)]

    cont_match = [('number_of_guests',operator.gt)]

    bool_match = [('guests_relationship',True),
                  ('parenting_guest',True),
                  ('pets_have',True),
                  ('smoking_household_acceptable',False),
                  ('drinking_household_acceptable',False),
                  ('substances_household_acceptable',False)]

    failed_constraints = []

    for cat, match_type,rev in categorical_match:

        hostkey = guest_host_field_assoc[cat]
        hostval = host[guest_host_field_assoc[cat]]
        guestkey = cat
        guestval = guest[cat]

        cf = categorical_filter(guestval,
                                hostval,
                                allcat = match_type,
                                reverse=rev)
        if cf:
            restriction_failed = [('hostQuestionKey',hostkey),
                                  ('hostResponseValue',hostval),
                                  ('guestQuestionKey',guestkey),
                                  ('guestResponseValue',guestval)]
            failed_constraints.append(OrderedDict(restriction_failed))


    for cont,op in cont_match:

        hostkey = guest_host_field_assoc[cont]
        hostval = host[guest_host_field_assoc[cont]]
        guestkey = cat
        guestval = guest[cont]

        if generic_filter(guestval,
                          hostval,
                          op):

            restriction_failed = [('hostQuestionKey',hostkey),
                                  ('hostResponseValue',hostval),
                                  ('guestQuestionKey',guestkey),
                                  ('guestResponseValue',guestval)]
            failed_constraints.append(OrderedDict(restriction_failed))


            #failed_constraints.append((cont,f'{guest[cont]} {op.__name__} {host[guest_host_field_assoc[cont]]}'))

    for boo,reverse in bool_match:

        hostkey = guest_host_field_assoc[boo]
        hostval = host[guest_host_field_assoc[boo]]
        guestkey = boo
        guestval = guest[boo]

        if bool_filter(guestval,
                       hostval,
                       reverse=reverse):

            restriction_failed = [('hostQuestionKey',hostkey),
                                  ('hostResponseValue',hostval),
                                  ('guestQuestionKey',guestkey),
                                  ('guestResponseValue',guestval)]
            failed_constraints.append(OrderedDict(restriction_failed))

            #failed_constraints.append((boo,None))

    return failed_constraints


def filter_hosts(guests, hosts):
    '''
    matchResults: [
        {
            guestId: 1,
            hostId: 1,
            restrictionsFailed: [
                {
                    hostQuestionId: 1,
                    hostResponseValue: 1,
                    guestQuestionId: 1,
                    guestResponseValue: 1,
                    reasonText: 'Can not smoke'
                }
            ],
            guestInterestLevel: GuestInterestLevel.Unknown,
            lastInterestUpdate: new Date()
        },
        {
            guestId: 2,
            hostId: 1,
            restrictionsFailed: [
                {
                    hostQuestionId: 1,
                    hostResponseValue: 'ok',
                    guestQuestionId: 1,
                    guestResponseValue: 'ok',
                    reasonText: 'Can not smoke'
                }
            ],
            guestInterestLevel: GuestInterestLevel.Unknown,
            lastInterestUpdate: new Date()
        },
    '''

    matchResults = []
    for guest in guests:
        for host in hosts:
            fc = filter_pair(guest['attributes'], host['attributes'])
            result = [('guestId',guest['id']),
                      ('hostId',host['id']),
                      ('restrictionsFailed',fc)]
            matchResults.append(OrderedDict(result))

    return matchResults


def main():

    #hosts = read_file('../fakehosts.csv',
    #                  converters = {"pets": literal_eval,
    #                                "allowed_pets":literal_eval})
    #guests = read_file('../fakeguests.csv',
    #                  converters = {"pets": literal_eval,
    #                                "pets_not_ok":literal_eval})
    hosts = read_json_file('../fakehosts21.json')
    guests = read_json_file('../fakeguests101.json')

    tstart = time.time()
    matches = filter_hosts(guests, hosts)
    print(f'filter took {time.time()-tstart:.3f}s')

    with open('matches_0118.json','w') as ofile:
        json.dump(matches,ofile,indent=1)


if __name__ == '__main__':
    main()
