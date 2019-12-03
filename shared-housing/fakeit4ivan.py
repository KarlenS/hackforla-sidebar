import numpy as np
import datetime
import json

import random

from faker import Faker
from faker.providers import BaseProvider

DEFAULT_WEIGHT = random.uniform(0, 1)

class Provider(BaseProvider):

    genders = ['male']*10+['female']*10+['mtf','ftm','gnc', '']

    age_groups = ['<17', '18-24', '25-34', '35-44',
                  '45-54', '55-64', '65-74', '>75']

    def gender(self):

        return {'field': 'gender',
                'values': [self.random_element(Provider.genders)],
                'values_not_in': [],
                'conflicts_with': [],
                'weight': None}

    def gender_preference(self):

        # this is pretty arbitrary, probably need a bultin same-gender
        # preference
        pref = set(self.random_elements(Provider.genders,length=5))

        # need to subset this and 
        nope = set(Provider.genders) - pref

        return {'field': 'gender_preference',
                'values': list(pref),
                'values_not_in': list(nope),
                'conflicts_with': ['gender'],
                'weight': DEFAULT_WEIGHT}

    def age(self,age):

        ages = Provider.age_groups
        indx = ages.index(age)

        # some hacky way of handling age preferences:
        # everyone wants a roommate within 20 years of their age group
        if indx == 0:
            not_allowed = ages[indx+1:]
        elif indx == 7:
            not_allowed = ages[:indx-2]
        else:
            not_allowed = ages[0:indx-1] + ages[indx+1:]

        return {'field': 'age',
                'values': [age],
                'values_not_in': not_allowed,
                'conflicts_with': ['age'],
                'weight': DEFAULT_WEIGHT/2.}

    def add_age_group(self, bdate):

        age = datetime.datetime.now().date() - bdate
        age = age.days/365.25

        age_groups = Provider.age_groups

        if age < 18:
            return age_groups[0]
        elif age >= 18 and age < 25:
            return age_groups[1]
        elif age >= 25 and age < 35:
            return age_groups[2]
        elif age >= 35 and age < 45:
            return age_groups[3]
        elif age >= 45 and age < 55:
            return age_groups[4]
        elif age >= 55 and age < 65:
            return age_groups[5]
        elif age >= 65 and age < 75:
            return age_groups[6]
        elif age >= 75:
            return age_groups[7]
        else:
            raise ValueError("Invalid age.")

    def kids(self):

        return {"field": 'kids',
                'value': [self.random_element([True]+[False]*4)],
                'value_not_in': [self.random_element([True]*3+[False])],
                'conflicts_with': ['kids'],
                'weight': DEFAULT_WEIGHT/3.}


    def drugs(self):

        drugs = ['marijuana', 'tobacco', 'alcohol','None']


        return {"field": 'kids',
                'value': [self.random_element(drugs)],
                'value_not_in': [self.random_element(drugs)],
                'conflicts_with': ['drugs'],
                'weight': DEFAULT_WEIGHT/3.}

    def basics(self,profile):

        age_group = self.add_age_group(profile['birthdate'])
        profile['birthdate'] = str(profile['birthdate'])
        profile['age_group'] = age_group
        profile['field'] = 'basics'

        del profile['address']
        del profile['username']
        del profile['mail']

        return profile

    def build_profile(self, *args):

        full_profile = {}
        for d in args:
            field = d['field']
            del d['field']
            full_profile[field] = d

        return full_profile

def main():

    fake = Faker()
    fake.add_provider(Provider)

    #with open('data.txt', 'r+') as outfile:
    for i in range(10):
        basic_profile = fake.simple_profile()
        basic_profile = fake.basics(basic_profile)
        profile = fake.build_profile(basic_profile,fake.gender(),fake.gender_preference(),
                                     fake.age(basic_profile['age_group']),fake.kids(),
                                     fake.drugs())
        print(profile)
 
    #        json.dump(profile, outfile)
    #        outfile.write('\n')

if __name__ == '__main__':
    main()
