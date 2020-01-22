'''
Generate fake host responses based on pre-selected questions
from the host application to be used in the filtering process.

code got ugly... but should work... will clean later
'''

import json
from collections import OrderedDict
from faker import Faker
from faker.providers import BaseProvider

import numpy as np
import pandas as pd
import datetime

import random

def exp_sampler(x = -1):
    return int(np.random.exponential(np.exp(x))//0.2)+1

class HostProvider(BaseProvider):

    genders = ['male']*10+['female']*10+['mtf','ftm','nb']
    housing_types = 5*['Single Family House']+5*['Multi-Unit']\
                    +3*['Apartment']+['Mobile Home']

    pet_stats = {'dogs':481572,'cats': 319229, 'birds': 35197,
                 'fish': 141980,'reptiles': 49112, 'other': 58662}

    cities = ['Beverly Hills, CA', 'Culver City, CA', 'Malibu, CA',
              'Santa Monica, CA', 'West Hollywood, CA']

    meta_faker = Faker()

    def gender(self):
        return ('gender', self.random_element(HostProvider.genders))


    def address_short(self):
        return ('address',self.random_element(HostProvider.cities))

    def languages(self):
        #this is a tough one- do significant number not speak english?
        #otherwise, what's the point here, are same-language speakers
        #a better match? if so, this is more a preference criterion.
        #also... super inefficient - not sure why moved this down...
        languages = pd.read_csv('languages.txt', delimiter='\t',
                               names=['language','total','good','bad'])

        languages['total'] = languages.total.apply(lambda x: int(x.replace(',','')))

        langlist = []

        fenglish = 0.48
        if np.random.binomial(n=1,p=fenglish):
            return ('languages',['English'])

        if np.random.binomial(n=1,p=0.8):
            langlist.append('English')

        n_draws = exp_sampler(x = -3)

        return ('languages', langlist +\
                            list(languages.sample(n=int(n_draws),
                                    weights='total',
                                    replace=False).language.unique()))

    def pets_have(self):

        fno_pets = 0.477
        if np.random.binomial(n=1,p=fno_pets):
            return ('pets_have',False)
        else:
            return ('pets_have',True)


    def pets_kind(self):
        #http://www.laalmanac.com/environment/ev21d.php

        n_draws = exp_sampler()
        pets = pd.DataFrame.from_dict(HostProvider.pet_stats,orient='index')
        return ('pets_kind', list(pets.sample(n=int(n_draws),
                            replace=True).index.unique().values))


    def pets_other(self):
        # for other: https://en.wikipedia.org/wiki/Exotic_pet
        other_pets = pd.read_csv('other_pets.txt')

        n_draws = exp_sampler(x=-2)
        return ('pets_other', list(other_pets.\
                                   sample(n=int(n_draws)).pet.values))

    def household_members(self,last_name=None):

        n_draws = exp_sampler(x = -2)
        first = True

        members = []

        for i in range(n_draws):

            info = OrderedDict()

            if first and np.random.binomial(n=1,p=0.9):
                info['name'] = HostProvider.meta_faker.first_name() +' '+ last_name
                info['age'] = int(self.random_element(np.arange(25,80,1)))
                info['relationship'] = 'partner'
                first = False
            elif np.random.binomial(n=1,p=0.05):
                info['name'] = HostProvider.meta_faker.name()
                info['age'] = int(self.random_element(np.arange(25,80,1)))
                info['relationship'] = 'partner'
            else:
                rel = 'child'
                info['name'] = HostProvider.meta_faker.first_name() +' '+ last_name
                info['age'] = int(self.random_element(np.arange(1,18,1)))
                info['relationship'] = 'child'

            members.append(info)

        return ('household_members',members)


    def housing_type(self):

        status = 'Owned ' if np.random.binomial(n=1,p=0.6) else 'Rented '
        return ('housing_type',status + self.random_element(HostProvider.housing_types))


    def employment_info(self):

        start_date = str(HostProvider.meta_faker.date_between(start_date="-10y",
                                                      end_date="-1y"))
        company = HostProvider.meta_faker.company()
        job = HostProvider.meta_faker.job()

        return ('employment_info',f'{job}, {company}, {start_date} to present')


    def interests(self):
        interest_list = [
            'cheesecakes','parrots','salsa dancing','extreme volunteering',
            'board games','chess','music','movies','martial arts','puzzles',
            'trashy tv','tinkering','sleeping','plants','food','basketball',
            'soccer','wasting time online']

        return ('interests',HostProvider.meta_faker.words(nb=4,
                                          ext_word_list=interest_list,
                                          unique=True))


    def references(self):

        f1name = HostProvider.meta_faker.first_name()
        f2name = HostProvider.meta_faker.first_name()
        l1name = HostProvider.meta_faker.last_name()
        l2name = HostProvider.meta_faker.last_name()

        email1 = f1name.lower() + '.' + l1name.lower()+'@gmail.com'
        email2 = f2name.lower() + '.' + l2name.lower()+'@gmail.com'
        phone1 = HostProvider.meta_faker.phone_number()
        phone2 = HostProvider.meta_faker.phone_number()

        ref1 = f'{f1name} {l1name}, Friend, {phone1}, {email1}'
        ref2 = f'{f2name} {l2name}, Friend, {phone2}, {email2}'

        return ('references',[ref1,ref2])


    def smoking_allowed(self):
        # assuming 5% of households allow indoor smoking
        findoor = 0.05
        return ('smoking_allowed', bool(np.random.binomial(n=1,p=findoor)))


    def smoking_residents(self):
        # assuming 25% of people smoke
        fsmoking = 0.25
        return ('smoking_residents', bool(np.random.binomial(n=1,p=fsmoking)))


    def drinking_residents(self):
        #assuming 54% of households consume alcohol 
        #http://www.publichealth.lacounty.gov/ha/reports/habriefs/v3i8_alcohol/alcohol.pdf
        falcohol = 0.54
        return ('drinking_residents', bool(np.random.binomial(n=1,p=falcohol)))

    def drinking_concerns(self):
        #assuming 10% are concerned 
        fconcern = 0.1
        isconcerned = bool(np.random.binomial(n=1,p=fconcern))

        if isconcerned:
            reason = HostProvider.meta_faker.sentence()
        else:
            reason = ''

        return ('drinking_concerns',(isconcerned,reason))

    def substances_residents(self):
        #assuming 25% of residents take substances
        fsubs = 0.25
        return ('substances_residents', bool(np.random.binomial(n=1,p=fsubs)))

    def substances_concerns(self):
        # assuming 10% are concerned
        #http://www.publichealth.lacounty.gov/ha/reports/habriefs/v3i8_alcohol/alcohol.pdf
        fconcern = 0.1
        isconcerned = bool(np.random.binomial(n=1,p=fconcern))

        if isconcerned:
            reason = HostProvider.meta_faker.sentence()
        else:
            reason = ''

        return ('substances_concerns', (isconcerned,reason))


    def duration_of_stay(self):
        # assuming 60/20 full/respite
        ffull = 0.6
        fboth = 0.2
        if np.random.binomial(n=1,p=fboth):
            return ('duration_of_stay', ['full','respite'])
        elif np.random.binomial(n=1,p=ffull):
            return ('duration_of_stay', ['full'])
        else:
            return ('duration_of_stay', ['respite'])


    def hosting_amount(self):
            return ('hosting_amount', exp_sampler())


    def pets_hosting(self):

        fpets = 0.2
        return ('pets_hosting', bool(np.random.binomial(n=1,p=fpets)))


    def pet_restrictions(self):
        # this is kind of stupid, but good enough
        n_draws = exp_sampler(x = -2)
        pets = pd.DataFrame.from_dict(HostProvider.pet_stats,orient='index')
        return ('pet_restrictions', list(pets.sample(n=int(n_draws),
                                    replace=True).index.unique().values))

    def youth_parenting(self):
        fparent = 0.1
        return ('youth_parenting', bool(np.random.binomial(n=1,p=fparent)))

    def youth_relationship(self):
        frel = 0.3
        return ('youth_relationship',bool(np.random.binomial(n=1,p=frel)))


def add_custom_text(full_profile):

    ####pets####
    pets_have = full_profile['pets_have']
    pets_hosting = full_profile['pets_hosting']
    pet_restrictions = full_profile['pet_restrictions']
    restriction_txt = ', '.join(pet_restrictions)

    if pets_have and pets_hosting:

        if pet_restrictions:
            pet_txt = "We have a pet and we'd love to host yours as "\
                      "long as it is not prohibited by our restrictions. "\
                      f"We allow {restriction_txt}."
        else:
            pet_txt = "We have a pet and we'd love to host yours."
    elif not pets_have and pets_hosting:

        if pet_restrictions:
            pet_txt = "We don't have pets, but we'd love to host yours as "\
                      "long as it is not prohibited by our restrictions. "\
                      f"We allow {restriction_txt}."
        else:
            pet_txt = "We don't have pets, but we'd love to host yours."

    elif pets_have and not pets_hosting:
        pet_txt = "Our pet(s) only need new human friends."

    elif not pets_have and not pets_hosting:
        pet_txt = "We provide a pet free environment."

    else:
        raise ValueError('what the hell....')

    ####smoking####
    smoking_residents = full_profile['smoking_residents']
    smoking_allowed = full_profile['smoking_allowed']

    if smoking_residents and smoking_allowed:
        smoking_txt = "We smoke in the house."
    elif not smoking_residents and smoking_allowed:
        smoking_txt = "We don't smoke, but we're ok with "\
                      "others smoking in the house."
    elif smoking_residents and not smoking_allowed:
        smoking_txt = "Our household has smokers but we don't "\
                      "smoke in the house."
    elif not smoking_residents and not smoking_allowed:
        smoking_txt = "We provide a smoke free environment."
    else:
        raise ValueError('what the hell....')

    ####drinking####
    drinking_residents = full_profile['drinking_residents']
    isconcerned,reason = full_profile['drinking_concerns']

    if drinking_residents and isconcerned:
        drinking_txt = "We drink alcohol. We have the following concerns "\
                       f"about drinking: {reason}"
    elif not drinking_residents and isconcerned:
        drinking_txt = "No one in the house drinks. We have the following"\
                       f"conerns about drinking: {reason}"
    elif drinking_residents and not isconcerned:
        drinking_txt = "We drink alcohol."
    elif not drinking_residents and not isconcerned:
        drinking_txt = "No one in the house drinks alcohol."
    else:
        raise ValueError('what the hell....')

    ####substances####

    substances_residents = full_profile['substances_residents']
    isconcerned,reason = full_profile['substances_concerns']

    if substances_residents and isconcerned:
        substances_txt = "We use substances. We have concerns about "\
                         f"substance use: {reason}"
    elif not substances_residents and isconcerned:
        substances_txt = "No one in the house uses substances. "\
                         f"We have concerns about substance use: {reason}"
    elif substances_residents and not isconcerned:
        substances_txt = "We use substances."
    elif not substances_residents and not isconcerned:
        substances_txt = "No one in the house uses substances."
    else:
        raise ValueError('what the hell....')

    ##################

    full_profile['pets_text'] = pet_txt
    full_profile['drinking_text'] = drinking_txt
    full_profile['smoking_text'] = smoking_txt
    full_profile['substances_text'] = substances_txt

    return full_profile

def build_host_profile(fake, *args):

    full_profile = OrderedDict()

    gender = fake.gender()[1]
    if gender == 'male':
        full_profile['first_name'] = fake.first_name_male()
    elif gender == 'female':
        full_profile['first_name'] = fake.first_name_female()
    else:
        full_profile['first_name'] = fake.first_name()

    full_profile['middle_initial'] = fake.first_name()[0]
    last_name = full_profile['last_name'] = fake.last_name()


    full_profile['dob'] = str(fake.date_of_birth(minimum_age=21,
                                                 maximum_age=90))

    full_profile['gender'] = gender

    full_profile['household_members'] =\
                fake.household_members(last_name=last_name)[1]

    ### pets with some logic...
    _, pets_have = fake.pets_have()
    full_profile['pets_have'] = pets_have

    if pets_have:
        _, pets_kind = fake.pets_kind()

        if 'other' in pets_kind:
            _, pets_other = fake.pets_other()
        else:
            pets_other = []

    else:
        pets_kind = []
        pets_other = []

    full_profile['pets_kind'] = pets_kind
    full_profile['pets_other'] = pets_other
    all_pets = pets_kind + pets_other
    try:
        all_pets.remove('other')
    except ValueError:
        pass
    full_profile['pets_list'] = all_pets
    ###



    full_profile['email'] = full_profile['first_name'].lower()\
                            +'.'+full_profile['last_name'].lower()+'@gmail.com'
    full_profile['phone'] = fake.phone_number()
    #full_profile['address'] = fake.address()[:-8]+'CA '\
    #                         +fake.postcode_in_state(state_abbr='CA')
    full_profile['address'] = fake.address_short()[1]

    if np.random.binomial(n=1,p=0.8):
        full_profile['contact_address'] = full_profile['address']
    else:
        full_profile['contact_address'] = fake.address()[:-8]+'CA '\
                                         +fake.postcode_in_state(state_abbr='CA')

    if np.random.binomial(n=1,p=0.6):
        full_profile['contact_method'] = 'email'
    else:
        full_profile['contact_method'] = 'phone'

    for field,val in args:
        full_profile[field] = val

    if not full_profile['pets_hosting']:
        full_profile['pet_restrictions'] = []
    else:
        full_profile['pet_restrictions'] = fake.pet_restrictions()[1]


    full_profile = add_custom_text(full_profile)


    if full_profile['hosting_amount'] == 1:
        full_profile['youth_parenting'] = False
        full_profile['youth_relationship'] = False
    else:
        full_profile['youth_parenting'] = fake.youth_parenting()[1]
        full_profile['youth_relationship'] = fake.youth_relationship()[1]


    #open ended responses
    full_profile['preferred_characteristics'] = fake.paragraph(
                                                    nb_sentences=3,
                                                    variable_nb_sentences=True
                                                )

    full_profile['hosting_interest'] = fake.paragraph(
                                          nb_sentences=2,
                                          variable_nb_sentences=True)

    full_profile['hosting_strenghts'] = fake.paragraph(
                                                    nb_sentences=2,
                                                    variable_nb_sentences=True)

    full_profile['hosting_challenges'] = fake.paragraph(
                                                    nb_sentences=4,
                                                    variable_nb_sentences=True)
    full_profile['host_intro'] = fake.paragraph(
                                                nb_sentences=6,
                                                variable_nb_sentences=True)

    return full_profile



def create_data(n_hosts = 20, filename='fakehosts21_v2.json'):

    fake = Faker()
    fake.add_provider(HostProvider)

    hosts = []

    host = {}
    for i in range(n_hosts):
        host['type'] = 'host'
        host['id'] = f'h{i}'

        profile = build_host_profile(fake,fake.housing_type(),
                                fake.employment_info(),fake.interests(),
                                fake.references(),fake.languages(),
                                fake.smoking_residents(),fake.smoking_allowed(),
                                fake.drinking_residents(),fake.drinking_concerns(),
                                fake.substances_residents(),fake.substances_concerns(),
                                fake.duration_of_stay(),fake.hosting_amount(),
                                fake.pets_hosting()
                               )
        host['attributes'] = profile
        hosts.append(json.loads(json.dumps(host)))

    with open(filename,'w') as ofile:
        json.dump(hosts,ofile,indent=1)
    #fake_data = pd.DataFrame.from_dict(rows, orient='columns')
    #fake_data.to_csv(filename,index=False)

if __name__ == '__main__':
    create_data()
