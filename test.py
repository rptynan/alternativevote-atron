#!/usr/bin/python3
import unittest
import random
from count import eliminate, tally, run_count, get_ballots_for_postition


class TestCount(unittest.TestCase):

    def test_tally(self):
        ballots = [{1: 'A', 2: 'B', 3: 'C'},
                   {1: 'B', 2: 'C', 3: ''},
                   {1: 'B', 2: 'C', 3: ''},
                   {1: 'B', 2: '', 3: ''},
                   {1: 'C', 2: '', 3: ''},
                   {1: 'C', 2: '', 3: ''}]
        results = tally(ballots, ['A', 'B', 'C'])
        self.assertEqual(results, {'A': 1, 'B': 3, 'C': 2})

    def test_eliminate(self):
        ballots = [{1: 'A', 2: 'B', 3: 'C'}, {1: 'B', 2: 'C', 3: ''}]
        ballots = eliminate(['B', 'C'], ballots)  # Eliminating A
        self.assertCountEqual(ballots,
                              [{1: 'B', 2: 'C', 3: ''},
                               {1: 'B', 2: 'C', 3: ''}])
        ballots = eliminate(['C'], ballots)  # Eliminating B
        self.assertCountEqual(ballots,
                              [{1: 'C', 2: '', 3: ''}, {1: 'C', 2: '', 3: ''}])
        ballots = eliminate([], ballots)  # Everyone's gone
        self.assertCountEqual(ballots, [])

    def test_run_count(self):
        votes = [
            # A
            {1: 'A', 2: 'B', 3: 'C'},
            {1: 'A', 2: 'B', 3: 'C'},
            {1: 'A', 2: 'B', 3: 'C'},
            # B
            {1: 'B', 2: 'A', 3: 'C'},
            {1: 'B', 2: 'C', 3: 'A'},
            {1: 'B', 2: '', 3: ''},
            # C
            {1: 'C', 2: 'A', 3: ''},
            {1: 'C', 2: 'A', 3: ''},
            {1: 'C', 2: 'A', 3: ''},
            # Hopefully people don't do this but if they do, we should shift
            # their highest preference up to 1.
            {1: '', 2: 'A', 3: ''},
            {1: '', 2: 'B', 3: ''},
        ]
        random.shuffle(votes)
        self.assertEqual(run_count('first_choice_p1', votes), ('A', 7))

    def test_get_ballots_for_postition(self):
        votes = [
            {'first_choice_p1': 'A', 'second_choice_p1': 'B', 'third_choice_p1': 'C'},
            {'first_choice_p1': 'B', 'second_choice_p1': '', },
            {'first_choice_p1': 'C', 'second_choice_p1': 'A', 'third_choice_p1': 'B'},
            {'first_choice_p2': 'X', 'second_choice_p2': 'Y', 'third_choice_p2': 'Z'},
            {'first_choice_p2': '', 'second_choice_p2': '', 'third_choice_p2': ''},
            {'first_choice_p2': 'X', },
        ]
        random.shuffle(votes)
        ballots = get_ballots_for_postition('p1', votes)
        self.assertCountEqual(ballots,
                              [{1: 'A', 2: 'B', 3: 'C'},
                               {1: 'B', 2: '', 3: ''},
                               {1: 'C', 2: 'A', 3: 'B'}, ])
        ballots = get_ballots_for_postition('p2', votes)
        self.assertCountEqual(ballots,
                              [{1: 'X', 2: 'Y', 3: 'Z'},
                               {1:  'X', 2: '', 3: ''}, ])


if __name__ == '__main__':
    unittest.main(verbosity=2)
