import numpy as np
from typing import List
from itertools import combinations

class Person:

    def __init__(self,person_id: int,responses: List = []):
        self.person_id = person_id
        self.responses = responses

    def pair_with_other(self, other: Person):

        score = 0

        for response in self.responses:

            try:
                resp_match = other.responses[response['id']]
            except KeyError:
                continue

            for val in response['value_not_in']:
                if val in resp_match['value']:
                    #can store this as a dict or something to have
                    #more detailed matching info
                    sore += response['weight']

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
            # probably just replace this with the matrix
            conflict_score += person.pair_with_other(other)

        return conflict_score


def build_conflict_matrix(person_list: List[Person]) -> np.matrix:

    n_people = len(person_list)
    conflict_matrix = np.full([n_people,n_people],np.inf)

    for i in range(n_people):
        for j in range(n_people):
            if i == j:
                conflict_matrix[i,j] = 0
            else:
                conlict_matrix[i,j] = person_list[i].pair_with_other(
                    person_list[j]
                )

    return conflict_matrix


def find_best_cluster(conflict_matrix: np.matrix,
                      n_people: int, n_iter: int) -> List[Person]:

    best_score = 0
    best_group = []
    #tried = []

    combs = combinations(range(conflict_matrix.shape[0])), n_people)
    #can also loop through all of these...

    #for _ in range(n_iter):
    for test_people in combs:

        score = 0

        #test_people = random.sample(range(0, conflict_matrix.shape[0]),
        #                            n_people)

        #while set(test_people) in tried:
        #    test_people = random.sample(range(0, conflict_matrix.shape[0]),
        #                                n_people)
        #tried.append(set(test_people))

        for i in range(n_people):
            for j in range(i+1,n_people):
                score += conflict_matrix(i,j)

        if score < best_score:
            best_score = score
            best_group = test_people

    return best_group, best_score
