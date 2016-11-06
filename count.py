#!/usr/bin/python3
import csv
import sys
import math

# RONs and None Vote are not equivalent, RON is a candidate, None Vote is just
# thrown out.
# Quota is per position not including people who voted none in everything
# If only two candidates are left we forego the quota
# If tie-break between lowest two candidates, look at all second preferences
# and tie-break on that.

# - None vote is empty string ''
# - Only up to three preferences, should be labeled
#   "first_choice_position_name", etc
# - I'm defining the following terms: A "ballot" refer to the ranked preference
#   of one voter for a single position, as opposed to a "vote" which refers to
#   one voter's ballots for all the positions
X_CHOICE_KEYS = {'first': 1, 'second': 2, 'third': 3}
FIRST_CHOICE_KEY = 'first_choice_'
RON = 'RON'
NONE_VOTE = ''


# Counts the first preference ballots for each candidate, returning a
# dictionary of candidate: number of first preferences.
# ballots - a list of dictionaries representing preference ballots,
#         e.g. [{1: 'A', 2: 'B', ...}, ...]
def tally(ballots, candidates):
    results = {candidate: 0 for candidate in candidates}
    for ballot in ballots:
        results[ballot[1]] += 1
    return results


# Eliminates candidate by redistributing all of his first_choice ballots to
# second_choice candidate (or to no one if no second_choice exists).
# position - a string, e.g. 'president', 'female_welfare'
# candidates_remaining - the name of the all the candidates that remain *i.e.
#                        not including the one we're eliminating!*
# ballots - a list of dictionaries representing preference ballots,
#         e.g. [{1: 'A', 2: 'B', ...}, ...]
def eliminate(candidates_remaining, ballots):
    result = []
    for ballot in ballots:
        # You need to run it for three times in case someone's voted like this:
        # {1: candidate, 2: candidate, 3: candidate}
        for i in range(3):
            if ballot[1] not in candidates_remaining:
                ballot = {1: ballot[2], 2: ballot[3], 3: NONE_VOTE}
        # If it's none vote, there are no more preferences, so throw it out
        if ballot[1] != NONE_VOTE:
            result.append(ballot)
    return result


# Runs alternate voting (AV) counting on the ballots for position.
# position - a string, e.g. 'president', 'female_welfare'
# ballots - a list of dictionaries representing preference ballots,
#         e.g. [{1: 'A', 2: 'B', ...}, ...]
def run_count(position, ballots):
    candidates = set([ballot[i] for i in [1, 2, 3] for ballot in ballots])
    if NONE_VOTE in candidates:
        candidates.remove(NONE_VOTE)  # isn't a candidate
        ballots = eliminate(candidates, ballots)
    quota = math.ceil(len(ballots) / 2)

    print('\n## Counting for position {0}, {1} votes cast, quota is {2}.'
          .format(position, len(ballots), quota))
    print('_Candidates standing for the position: {0}_'
          .format(', '.join(candidates)))

    round_num = 0
    while True:
        round_num += 1
        round_results = tally(ballots, candidates)
        round_results.pop('', None)
        print('\n### Round {0} Results:'.format(round_num))
        print('\nCandidate | Votes\n:-- | --:')
        for candidate, num_votes in round_results.items():
            print('{0} | {1}'.format(candidate, num_votes))

        # Check for ties, output message to warn person to checkover results
        vote_nums = [num for candidate, num in round_results.items()]
        if len(vote_nums) != len(set(vote_nums)):
            print('WARNING! There\'s a tie in this round\'s results. It might '
                  'not affect anything, but if it does you might have to '
                  'manually count.')

        # See if quota reach or if we need to eliminate
        highest_candidate = max(round_results.keys(),
                                key=lambda k: round_results[k])
        lowest_candidate = min(round_results.keys(),
                               key=lambda k: round_results[k])
        if round_results[highest_candidate] >= quota:
            print('\n**Candidate {0}, having exceded the quota on this round, '
                  'is duly elected.**'.format(highest_candidate))
            return (highest_candidate, round_results[highest_candidate])
        else:
            print('\n_Candidate {0}, having the lowest number of votes, is '
                  'eliminated and their votes will be redistributed to the '
                  'second highest preference candidate on each._'
                  .format(lowest_candidate))
            candidates.remove(lowest_candidate)
            ballots = eliminate(candidates, ballots)


# Returns a list of the form [{1: 'A', 2: 'B', ...}, ...] indicating ballot
# preferences for the position given, exluding ballots which are all none votes
# position - a string, e.g. 'president', 'female_welfare'
# raw votes - a list of dictionaries of preference ballots for all the
#             positions
def get_ballots_for_postition(position, raw_votes):
    # Create list of dictionaries of each ballot for that position
    # X_CHOICE_KEYS converst 'first_choice_position' to 1, etc
    ballots = []
    for vote in raw_votes:
        ballot = {X_CHOICE_KEYS[pref.split('_')[0]]: candidate
                  for pref, candidate in vote.items()
                  if '_' + position in pref}
        # Fill in second/third choices if not present
        ballot[2] = ballot[2] if 2 in ballot else NONE_VOTE
        ballot[3] = ballot[3] if 3 in ballot else NONE_VOTE
        ballots.append(ballot)
    # Exclude empty ballots so we can get the quota of people who voted for
    # this position, not voted overall
    ballots = [ballot for ballot in ballots
               if not all(candidate == NONE_VOTE
                          for pref, candidate in ballot.items())]
    return ballots


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ./count.py FILE')
        print('where FILE is a CSV file exported from Drupal\'s webform '
              'module, see example')
        exit(1)

    title = ''
    raw_votes = []
    with open(sys.argv[1], 'r') as csv_file:
        title = csv_file.readline()
        next(csv_file)  # Skip junk line so fieldnames are next
        reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        raw_votes = [row for row in reader]
    print('# ' + title.replace('"', '').replace(',', ''))

    # Find the positions being contested by looking at all first_choice_* keys
    positions = [x.replace(FIRST_CHOICE_KEY, '')
                 for x in raw_votes[0] if FIRST_CHOICE_KEY in x]
    print('Counting votes for the following positions: {}\n'.format(positions))

    for position in positions:
        ballots = get_ballots_for_postition(position, raw_votes)
        run_count(position, ballots)
