'''
Generate fake guest responses based on pre-selected questions
from the guest application to be used in the filtering process.
'''
from collections import OrderedDict
import json
from faker import Faker
from faker.providers import BaseProvider

import numpy as np
import pandas as pd

import random

def exp_sampler(x = -1):
    return int(np.random.exponential(np.exp(x))//0.2)+1

class Provider(BaseProvider):

    genders = ['male']*10+['female']*10+['transgender','nonbinary']

    pet_stats = {'dog':481572,'cat': 319229, 'bird': 35197,
                 'fish': 141980,'reptile': 49112, 'other': 58662}

    pet_allergies = {'dog': 5, 'cat': 10, 'reptile': 1}

    meta_faker = Faker()

    def gender(self):
        return ('gender', self.random_element(Provider.genders))

    def languages(self):
        #this is a tough one- do significant number not speak english?
        #otherwise, what's the point here, are same-language speakers
        #a better match? if so, this is more a preference criterion.
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


    def household_members(self,last_name=None):

        n_draws = exp_sampler(x = -2) - 1
        first = True

        members = []

        for i in range(n_draws):

            info = OrderedDict()

            if first and np.random.binomial(n=1,p=0.8):
                info['name'] = Provider.meta_faker.first_name() +' '+ last_name
                info['age'] = int(self.random_element(np.arange(25,80,1)))
                info['relationship'] = 'sibling'
                first = False
            elif np.random.binomial(n=1,p=0.1):
                info['name'] = Provider.meta_faker.name()
                info['age'] = int(self.random_element(np.arange(25,80,1)))
                info['relationship'] = 'partner'
            else:
                rel = 'child'
                info['name'] = Provider.meta_faker.first_name() +' '+ last_name
                info['age'] = int(self.random_element(np.arange(1,18,1)))
                info['relationship'] = 'child'

            members.append(info)

        return ('household_members',members)


    def pets_have(self):

        fno_pets = 0.877
        if np.random.binomial(n=1,p=fno_pets):
            return ('pets_have',False)
        else:
            return ('pets_have',True)


    def pets_kind(self):
        #http://www.laalmanac.com/environment/ev21d.php

        n_draws = exp_sampler(x=-2)
        pets = pd.DataFrame.from_dict(Provider.pet_stats,orient='index')
        return ('pets_kind', list(pets.sample(n=int(n_draws),
                            replace=True).index.unique().values))



    def pets_other(self):
        # for other: https://en.wikipedia.org/wiki/Exotic_pet
        other_pets = pd.read_csv('other_pets.txt')

        n_draws = exp_sampler(x=-3)
        return ('pets_other', list(other_pets.\
                                   sample(n=int(n_draws)).pet.values))

    def employed(self):
        femployed = 0.65
        return ('employed', bool(np.random.binomial(n=1,p=femployed)))

    def employment_info(self):

        start_date = str(Provider.meta_faker.date_between(start_date="-10y",
                                                      end_date="-1y"))
        company = Provider.meta_faker.company()
        job = Provider.meta_faker.job()

        return ('employment_info',f'{job}, {company}, {start_date} to present')

    def in_school(self):
        fschool = 0.40
        return ('in_school', bool(np.random.binomial(n=1,p=fschool)))

    def school_info(self):
        return ('school_info', Provider.meta_faker.sentence())

    def smoking_guest(self):
        fsmoking = 0.25
        return ('smoking_guest', bool(np.random.binomial(n=1,p=fsmoking)))

    def smoking_household_acceptable(self):
        # assuming 70% not ok with indoor smoking
        findoor = 0.3
        return ('smoking_household_acceptable',
                bool(np.random.binomial(n=1,p=findoor)))

    def drinking_guest(self):
        #assuming 54% of households consume alcohol
        #http://www.publichealth.lacounty.gov/ha/reports/habriefs/v3i8_alcohol/alcohol.pdf
        falcohol = 0.54
        return ('drinking_guest', bool(np.random.binomial(n=1,p=falcohol)))

    def drinking_concerns(self):
        #assuming 10% are concerned
        fconcern = 0.1
        isconcerned = bool(np.random.binomial(n=1,p=fconcern))

        if isconcerned:
            reason = Provider.meta_faker.sentence()
        else:
            reason = ''

        return ('drinking_concerns',(isconcerned,reason))

    def drinking_household_acceptable(self):
        #http://www.publichealth.lacounty.gov/ha/reports/habriefs/v3i8_alcohol/alcohol.pdf
        falcohol = 0.8
        return ('drinking_household_acceptable',
                bool(np.random.binomial(n=1,p=falcohol)))

    def substances_guest(self):
        #assuming 20% of guests take substances
        fsubs = 0.2
        return ('substances_guest', bool(np.random.binomial(n=1,p=fsubs)))

    def substances_concerns(self):
        # assuming 10% are concerned
        fconcern = 0.1
        isconcerned = bool(np.random.binomial(n=1,p=fconcern))

        if isconcerned:
            reason = Provider.meta_faker.sentence()
        else:
            reason = ''

        return ('substances_concerns', (isconcerned,reason))


    def substances_household_acceptable(self):
        #http://www.publichealth.lacounty.gov/ha/reports/habriefs/v3i8_alcohol/alcohol.pdf
        falcohol = 0.8
        return ('substances_household_acceptable',
                bool(np.random.binomial(n=1,p=falcohol)))

    def mental_illness(self):
        #assuming 25% of guests take substances
        fmh = 0.25
        return ('mental_illness', bool(np.random.binomial(n=1,p=fmh)))

    def duration_of_stay(self):
        # assuming 80/20 full/respite
        ffull = 0.8
        if np.random.binomial(n=1,p=ffull):
            return ('duration_of_stay', ['full'])
        else:
            return ('duration_of_stay', ['respite'])


    def number_of_guests(self):
            return ('number_of_guests', exp_sampler(x=-2))


    def host_pets(self):
        # this is kind of stupid, but good enough
        fpets = 0.8
        if np.random.binomial(n=1,p=fpets):
            return ('host_pets', True)
        else:
            return ('host_pets', False)


    def host_pet_restrictions(self):
        n_draws = exp_sampler(x = -2)
        pets = pd.DataFrame.from_dict(Provider.pet_allergies,orient='index')
        not_ok = list(pets.sample(n=int(n_draws),replace=True).index.unique().values)
        return ('host_pet_restrictions',not_ok)

#    def parenting_guest(self):
#        fparent = 0.2
#        return ('guest_is_parent', np.random.binomial(n=1,p=fparent))
#
#    def guests_relationship(self):
#        frel = 0.3
#        return ('guest_in_relationship',np.random.binomial(n=1,p=frel))

def add_custom_text(full_profile):

    ####pets####
    pets_have = full_profile['pets_have']
    host_pets = full_profile['host_pets']

    if pets_have and host_pets:
        pet_txt = "I have pet(s), and would love to live with more pets."
    elif not pets_have and host_pets:
        pet_txt = "I have no pets and would love to live with pets."
    elif pets_have and not host_pets:
        pet_txt = "My pet(s) only need new human friends."
    elif not pets_have and not host_pets:
        pet_txt = "I have no pets and prefer to live in a pet free place."
    else:
        raise ValueError('what the hell....')

    ####smoking####
    smoking_guest = full_profile['smoking_guest']
    smoking_household_acceptable = full_profile['smoking_household_acceptable']

    if smoking_guest and smoking_household_acceptable:
        smoking_txt = "I smoke, and if permitted, I'm fine with indoor smoking."
    elif not smoking_guest and smoking_household_acceptable:
        smoking_txt = "I don't smoke, but I'm find with others smoking indoors."
    elif smoking_guest and not smoking_household_acceptable:
        smoking_txt = "I smoke cigerettes, but I prefer a smoke free "\
                      "environment indoors."
    elif not smoking_guest and not smoking_household_acceptable:
        smoking_txt = "I do not smoke cigerettes, and I prefer a smoke-free "\
                      "environment indoors."
    else:
        raise ValueError('what the hell....')

    ####drinking####
    drinking_guest = full_profile['drinking_guest']
    drinking_household_acceptable =\
            full_profile['drinking_household_acceptable']

    isconcerned,reason = full_profile['drinking_concerns']

    if isconcerned:
        concern_txt = f" I have concerns about my drinking: {reason}"
    else:
        concern_txt = ""

    if drinking_guest and drinking_household_acceptable:
        drinking_txt = "I drink alcohol, and I'm open to other people in "\
                       f"the household drinking alcohol.{concern_txt}"
    elif not drinking_guest and drinking_household_acceptable:
        drinking_txt = "I don't drink alcohol, but I'm open to other people "\
                       f"in the household drinking alcohol.{concern_txt}"
    elif drinking_guest and not drinking_household_acceptable:
        drinking_txt = "I drink alcohol, but I'm not open to other people in "\
                       f"the household drinking alcohol.{concern_txt}"
    elif not drinking_guest and not drinking_household_acceptable:
        drinking_txt = "I don't drink alcohol and prefer an alcohol-free "\
                       f"environment.{concern_txt}"
    else:
        raise ValueError('what the hell....')

    ####substances####

    substances_guest = full_profile['substances_guest']
    substances_household_acceptable = full_profile['substances_household_acceptable']
    isconcerned,reason = full_profile['substances_concerns']

    if isconcerned:
        concern_txt = f" I have concerns about my substance use: {reason}"
    else:
        concern_txt = ""

    if substances_guest and substances_household_acceptable:
        substances_txt = "I use substances, and I'm open to other people "\
                         f"in the household using substances.{concern_txt}"
    elif not substances_guest and substances_household_acceptable:
        substances_txt = "I don't use substances, but I'm open to other people "\
                         f"in the household using substances.{concern_txt}"
    elif substances_guest and not substances_household_acceptable:
        substances_txt = "I use substances, but I'm not open to other people "\
                         f"in the household using substances.{concern_txt}"
    elif not substances_guest and not substances_household_acceptable:
        substances_txt = "I don't use substances and prefer a substance-free "\
                         f"environment.{concern_txt}"
    else:
        raise ValueError('what the hell....')

    ##################

    full_profile['pets_text'] = pet_txt
    full_profile['drinking_text'] = drinking_txt
    full_profile['smoking_text'] = smoking_txt
    full_profile['substances_text'] = substances_txt

    return full_profile



def build_guest_profile(fake, *args):
    '''
        first_name
        middle_initial
        last_name
        dob
        gender
        household_members
        pets_have
        pets_kind
        pets_other
        host_pets
        host_pet_restrictions
        email
        phone
        contact_method
        employed
        employment_info
        in_school
        school_info
        languages
        duration_of_stay
        smoking_guest
        smoking_household_acceptable
        drinking_guest
        drinking_concerns
        drinking_household_acceptable
        substances_guest
        substances_concerns
        substances_household_acceptable
        mental_illness
        mental_illness_description
        mental_illness_care
        guest_stay_statement
        guest_stay_relationship
        guest_challenges
        guest_intro
    '''
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


    full_profile['dob'] = str(fake.date_of_birth(minimum_age=18,
                                                 maximum_age=26))

    full_profile['gender'] = gender

    full_profile['household_members'] =\
                fake.household_members(last_name=last_name)[1]

    full_profile['email'] = full_profile['first_name'].lower()\
                            +'.'+full_profile['last_name'].lower()+'@gmail.com'
    full_profile['phone'] = fake.phone_number()

    if np.random.binomial(n=1,p=0.6):
        full_profile['contact_method'] = 'email'
    else:
        full_profile['contact_method'] = 'phone'

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

    _,host_pets = fake.host_pets()
    full_profile['host_pets'] = host_pets
    if host_pets:
        full_profile['host_pet_restrictions'] = fake.host_pet_restrictions()[1]
    else:
        full_profile['host_pet_restrictions'] = []

    for field,val in args:
        full_profile[field] = val


    full_profile = add_custom_text(full_profile)


    if full_profile['mental_illness']:
        #maybe migrate below to the above class for cleaning... 
        full_profile['mental_illness_description'] = fake.sentence()
        #assuming 60% receive mental health care
        full_profile['mental_illness_care'] = bool(np.random.binomial(n=1,p=0.6))
    else:
        full_profile['mental_illness_description'] = ''
        full_profile['mental_illness_care'] = False

    number_of_guests = len(full_profile['household_members']) + 1
    full_profile['number_of_guests'] = number_of_guests

    ### logic for consistent parenting/relationsihp guests
    if number_of_guests < 2:
        full_profile['parenting_guest'] = False
        full_profile['guests_relationship'] = False
    else:
        relationships = [person['relationship'] for person in full_profile['household_members']]

        full_profile['parenting_guest'] =\
                True if 'child' in relationships else False

        full_profile['guests_relationship'] =\
                True if 'partner' in relationships else False


    full_profile['guest_stay_statement'] = fake.paragraph(
                                        nb_sentences=5,
                                        variable_nb_sentences=True)
    full_profile['guest_stay_relationship'] = fake.paragraph(
                                        nb_sentences=3,
                                        variable_nb_sentences=True)
    full_profile['guest_challenges'] = fake.paragraph(
                                        nb_sentences=3,
                                        variable_nb_sentences=True)
    full_profile['guest_intro'] = fake.paragraph(
                                        nb_sentences=6,
                                        variable_nb_sentences=True)

    return full_profile


def create_data(n_guests = 100, filename='fakeguests101.json'):

    fake = Faker()
    fake.add_provider(Provider)

    guests = []

    for i in range(n_guests):
        guest = OrderedDict()
        guest['type'] = 'guest'
        guest['id'] = f'g{i}'
        profile = build_guest_profile(fake,fake.employed(),fake.employment_info(),
                                fake.in_school(),fake.school_info(),
                                fake.languages(),
                                fake.smoking_guest(),
                                fake.smoking_household_acceptable(),
                                fake.drinking_guest(),fake.drinking_concerns(),
                                fake.drinking_household_acceptable(),
                                fake.substances_guest(),fake.substances_concerns(),
                                fake.substances_household_acceptable(),
                                fake.duration_of_stay(),fake.mental_illness())

        guest['attributes'] = profile
        guests.append(json.loads(json.dumps(guest)))

    with open(filename,'w') as ofile:
        json.dump(guests,ofile,indent=1)
    #rows.append(profile)

    #fake_data = pd.DataFrame.from_dict(rows, orient='columns')
    #fake_data.to_csv(filename,index=False)


if __name__ == '__main__':
    create_data()
