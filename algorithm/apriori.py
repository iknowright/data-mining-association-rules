class Apriori():
    def __init__(self):
        pass

    def _create_candidate1(self, data):
        """
        Find unique items from dataset (Also initial candidate)
        """

        initial_candidate = []
        for transaction in data:
            for item in transaction:
                if not [item] in initial_candidate:
                    initial_candidate.append([item])
        initial_candidate.sort()
        return initial_candidate


    def _scan_for_frequent(self, data, candidate_k, minsup):
        """
        Given a given k-itemset candidate, return frequent set that support is greater than minimun
        """

        support_count = {}
        # checking db for given itemset support count
        for transaction in data:
            for candidate in map(frozenset, candidate_k):
                if candidate.issubset(transaction):
                    if not candidate in support_count:
                        support_count[candidate] = 1
                    else:
                        support_count[candidate] +=1

        total_txs = len(data)  # number of transactions

        # filter itemset from candidate that has greater support value than minimun
        frequent_set  = []
        itemset_support = {}
        for key in support_count:
            support = float(support_count[key] / total_txs)
            if support >= minsup:
                frequent_set.insert(0, key)
            itemset_support[key] = support
        return frequent_set, itemset_support


    def _apriori_generator(self, frequent_set, k):
        """
        Transform given frequent to new k-itemset candidate
        """
        new_candidate_k = []
        frequent_set_len = len(frequent_set)
        for i in range(frequent_set_len):
            for j in range(i + 1, frequent_set_len):
                L1 = list(frequent_set[i])[: k-2]
                L2 = list(frequent_set[j])[: k-2]
                L1.sort()
                L2.sort()
                if L1 == L2:
                    new_candidate_k.append(frequent_set[i] | frequent_set[j])
        return new_candidate_k


    def _apriori(self, data, minsup):
        """
        Description:
            Run Apriori algorithm on given dataset and minimun support

        Arguments:
            data: Data for Apriori algorithm to run
                ```
                [[1, 2, 3],
                 [2],
                 [3,4,5]]
            minsup: Minimun support for finding frequent itemset

        Return:
            total_frequent_set: frequent itemsets found in the dataset
            itemset_support: support value for all the itemset in the dataset
        """

        # Init Phase:
        # initial candidate will just be unique items found in the dataset
        candidate_1 = self._create_candidate1(data)

        # transfer `list` of `list` dataset to `list` of `set` dataset
        data_set = list(map(set, data))

        # given initial candidate (candidate_1), filter items that have support greater than `minsup`
        # and return item's support as well
        frequent_set, itemset_support = self._scan_for_frequent(data_set, candidate_1, minsup)

        # Recursion Phase:
        total_frequent_set = [frequent_set]  # initialize first iteration frequent set (acquired from init candidate)
        k = 2  # Apriori algorithm starts from `k_itemset`, minimun k value should be 2

        # if frequent_set from candidate_1 is not empty, start the recursion
        while (len(total_frequent_set[k-2]) > 0):

            # by passing current frequent k-1_itemset to apriori generator, it will return new candidate k_itemset
            candidate_k = self._apriori_generator(total_frequent_set[k-2], k)

            # by having candidate k_itemset, scan through dataset which filter candidate itemset to frequent itemset
            k_frequent_set, k_itemset_support = self._scan_for_frequent(data_set, candidate_k, minsup)

            itemset_support.update(k_itemset_support)  # update global itemset support value
            # when there is nothing in the frequent set, it means recursion is over.
            if len(k_frequent_set) == 0:
                break

            # expand total_frequent_set by frequent set found in this iteration
            total_frequent_set.append(k_frequent_set)

            # k value grows by one in every iteration
            k += 1

        # after all, return total frequent set and itemset support
        return total_frequent_set, itemset_support


    def generateFrequentSet(self, data, minsup):
        # transfer chunk data to single frequent set list
        total_frequent_set_in_chunk, itemset_support = self._apriori(data, minsup=minsup)
        total_frequent_set = []
        for frequent_set in total_frequent_set_in_chunk:
            for itemset in frequent_set:
                total_frequent_set.append(itemset)

        return total_frequent_set, itemset_support
