import numpy as np
from typing import List

class Person:

    def __init__(self,person_id: int,responses: List = []):
        self.person_id = person_id
        self.responses = responses

    def pair_with_other(self, other: Person):

        score = 0

        for response in self.responses:
            score += other.responses[response.conflict]

        return score


class Cluster:

    def __init__(self,person_list: List = [], cluster_score int: = 0):
        self.person_list = person_list
        self.cluster_score = cluster_score

    def add_person(self, person: Person):
        self.person_list.append(person)
        self.cluster_score += _get_conflict_score(self, person)

    def _get_conflict_score(self, person: Person) -> int:

        conflict_score = 0
        for other in self.person_list:
            conflict_score += person.pair_with_other(other)

        return conflict_score


def build_conflict_matrix(person_list: List):

    n_people = len(person_list)
    conflict_matrix = np.zeros([n_people,n_people])
