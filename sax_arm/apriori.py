
from itertools import combinations, chain
import pandas as pd


class Transactions():
    """
    Transactions manager
    """

    def __init__(self, transactions):
        """
        transactions = list of transactions
        """
        self.n_transactions = 0  # Total number of transactions
        self.items = []  # Individual transactions
        self.transactions_map = {}  # Indices of individual transactions

        for transaction in transactions:
            self.add_transaction(transaction)

    def add_transaction(self, transaction):
        for item in transaction:
            if item not in self.transactions_map:
                self.items.append(item)
                self.transactions_map[item] = set()
            self.transactions_map[item].add(self.n_transactions)
        self.n_transactions += 1

    def compute_support(self, candidate):
        """
        Computes the support for a candidate transaction.
        Support is computed by counting the indices of the intersection
        between items in the transaction. 
        """

        for i_item, item in enumerate(candidate):
            item_indexes = self.transactions_map.get(item)

            # If the candidate transaction cannot be found in the data
            if item_indexes == None:
                return 0

            # Otherwise, find the number of times the items appear
            # in the transactions
            else:
                if i_item == 0:
                    indexes = item_indexes
                else:
                    indexes = indexes.intersection(item_indexes)

        return len(indexes)/self.n_transactions

    def initial_candidates(self):
        """
        Initial candidates.
        """
        return [frozenset([item]) for item in self.items]


def apriori_gen(candidates, k):
    """
    Takes list of itemsets of size k and returns a list of all (k+1)-itemsets.
    A new itemset is added to the new list of candidates if all of its 
    subsets can be generated from the list of previous candidates.

    join is first created as a generator as it saves memory space. 
    """
    #############
    # Join step #
    #############

    # 'Removes' the frozenset type
    join = sorted(frozenset(chain.from_iterable(candidates)))
    # Generates new candidates
    join = (frozenset(x) for x in combinations(join, k))

    ##############
    # Prune step #
    ##############

    # if k==2, all subsets are of size k=1 and are necessarily present in
    # the list of previous candidates
    if k == 2:
        return list(join)
    else:
        new_candidates = [
            candidate for candidate in join
            if all(
                frozenset(x) in join
                for x in combinations(candidate, k-1))
        ]

    return new_candidates


def compute_supports(manager, min_supp):
    """
    Computes the support for each itemsets. New candidates are generated using
    Agrawal et. al.'s apriori_gen function.

    Inputs:
    - manager = Transaction object containing transactions informations.
    - min_supp = Transaction minimal support. Transactions with a support
    below this value will not be taken into consideration.

    Output:
    - Dictionary of transactions and their support. 
    """

    supports = {}

    candidates = manager.initial_candidates()

    k = 1
    while candidates:
        relations = set()

        for candidate in candidates:
            support = manager.compute_support(candidate)

            # Candidates with a low support are not selected
            if support < min_supp:
                continue

            relations.add(frozenset(candidate))
            supports[candidate] = support

        k += 1
        candidates = apriori_gen(relations, k)

    return supports


def compute_rules(manager, supports, min_conf):
    """
    Mines association rules to discover frequent patterns of deviant events
    that occur simultaneously.

    Inputs:
    - manager = Transaction object containing transactions informations.
    - supports = Dictionary of events and their support returned by the 
    compute_supports function.
    - min_conf = Rule minimal confidence. Rules with a confidence below this
    value will be filtered out from the resulting DataFrame.

    Output:
    - DataFrame with association rules and their metrics (support, confidence,
    lift) sorted by descending support.  
    """

    data = {
        'Rule': [],
        'Support': [],
        'Confidence': [],
        'Lift': []
    }

    # Iterate over transactions
    for items in supports:

        # Can't find rules if there is only one item in the set
        if len(items) == 1:
            continue

        # If the set contains more than one item
        else:
            sorted_items = sorted(items)

            # Create rules for each possible subset in items
            for length in range(1, len(items)):

                for combination in combinations(sorted_items, length):
                    A = frozenset(combination)
                    B = frozenset(items.difference(A))

                    # Compute metrics for each rule
                    support = supports[items]
                    confidence = support/manager.compute_support(A)
                    lift = confidence/manager.compute_support(B)

                    data['Rule'].append(f'{set(A)} --> {set(B)}')
                    data['Support'].append(support)
                    data['Confidence'].append(confidence)
                    data['Lift'].append(lift)

    # Return filtered results using the min_conf criteria
    rules = pd.DataFrame(data=data)

    return rules.loc[rules['Confidence'] >= min_conf].sort_values('Support', ascending=False)


def apriori(B, min_supp, min_conf=0):
    """
    A priori algorithm, as defined in Agrawal et. al. (1984). This implementation
    is heavily inspired by: https://github.com/ymoch/apyori/blob/master/apyori.py

    Contrary to Park et. al., support for an event A is computed as:
    support(A) = (number of transactions in which A appear) / (total number of 
    transactions). 
    Park et. al. rather use the number of time segments as the denominator.

    Inputs:
    - basket = Symbol Basket, defined in Park et. al. (2019).
    - min_supp = minimal support for a deviant event to be taken into
    consideration

    Output:
    - DataFrame with association rules and their metrics (support, confidence,
    lift) sorted by descending support.  
    """

    manager = Transactions(B)

    supports = compute_supports(manager, min_supp)

    rules = compute_rules(manager, supports, min_conf)

    return rules
