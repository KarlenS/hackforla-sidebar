import numpy as np

from faker import Faker
from faker.providers import BaseProvider

class Provider(BaseProvider):

    genders = ['male']*10+['female']*10+['mtf','ftm','gnc', '']

    def gender(self):

        return {'field': 'gender',
                'values': [self.random_element(Provider.genders)],
                'values_not_in': [],
                'conflicts_with': []}

    def gender_preference(self):

        return {'field': 'gender',
                'values': [self.random_element(Provider.genders)],
                'values_not_in': [],
                'conflicts_with': []}


def main():

    fake = Faker()
    fake.add_provider(Provider)

    for i in range(10):
        print(fake.gender())

    #model = {
    #    "field": "gender_preference",
    #    "values": [],
    #    "values_not_in": []
    #    "constraint_fields": ['gender']
    #}

if __name__ == '__main__':
    main()
