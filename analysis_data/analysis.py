import argparse
import time

from algorithm.apriori import Apriori
from algorithm.fpgrowth import FPGrowth


def execution_timer(func):
    """
    timer for execution
    """

    def wrapper(*args):
        start = time.time()
        func_ret = func(*args)
        elapsed = time.time() - start
        return func_ret, elapsed
    return wrapper


class Associator():
    def __init__(self):
        pass

    def _generate_candidate(self, k_itemset, k):
        """Given k-itemset frequent set, generate all possible k+1 itemset candidate"""
        return_candidate_list = []
        k_itemset_length = len(k_itemset)
        for i in range(k_itemset_length):
            for j in range(i+1, k_itemset_length):
                L1 = list(k_itemset[i])[: k-2]
                L2 = list(k_itemset[j])[: k-2]
                L1.sort()
                L2.sort()
                if L1 == L2:
                    return_candidate_list.append(k_itemset[i] | k_itemset[j])
        return return_candidate_list


    def _calcConf(self, frequent_set, header, itemset_support, total_generated_rules, minconf):
        '''
        Description:
            Calculate confidence
        Args:
            frequent_set: frequent set of data
            header: frequent set elements
            itemset_support: itemsets' support
            total_generated_rules: final rules place holder
            minconf: minimun confidence to accpet rules
        Returns:
            filtered_header: set elements that confidence greater than minconf
        '''

        filtered_header = []
        for conseq in header:
            try:
                conf = itemset_support[frequent_set] / itemset_support[frequent_set - conseq]
                if conf >= minconf:
                    total_generated_rules.append((frequent_set - conseq, conseq, conf))
                    filtered_header.append(conseq)
            except:
                pass
        return filtered_header

    def _rulesFromConseq(self, itemset, header, itemset_support, total_generated_rules, minconf):
        """
        Description:
            Recursively generate rules

        Args:
            itemset: frequent k-itemset
            header: k-itemset frequent set elements
            itemset_support: itemsets' support
            total_generated_rules: final rules place holder
            minconf: minimun confidence to accpet rules
        """

        sub_itemset_length = len(header[0])
        if (len(itemset) > (sub_itemset_length + 1)):
            k_by_1_elements = self._generate_candidate(header, sub_itemset_length+1)
            k_by_1_elements = self._calcConf(itemset, k_by_1_elements, itemset_support, total_generated_rules, minconf)
            if (len(k_by_1_elements) > 1):
                self._rulesFromConseq(itemset, k_by_1_elements, itemset_support, total_generated_rules, minconf)

    def _generateRules(self, frequent_set, itemset_support, minconf):
        """
        Description:
            Generate rules given all the frequent itemset
        Args:
            L 頻繁項集列表
            supportData 頻繁項集支援度的字典
            minConf 最小置信度
        Returns:
            bigRuleList 可信度規則列表（關於 (A->B+置信度) 3個欄位的組合）
        """

        final_total_rules = []
        for itemset in frequent_set:
            itemset_elements = [frozenset([item]) for item in itemset]
            if (len(itemset) > 2):
                self._rulesFromConseq(itemset, itemset_elements, itemset_support, final_total_rules, minconf)
            elif len(itemset) == 2:
                self._calcConf(itemset, itemset_elements, itemset_support, final_total_rules, minconf)
        return final_total_rules


    @execution_timer
    def generate_rules(self, algorithm, data, minsup, minconf):
        frequent_set, itemset_support = algorithm.generateFrequentSet(data, minsup)

        # Generate association rules
        rules = self._generateRules(frequent_set, itemset_support, minconf=minconf)
        rules.sort(key=lambda r: (r[2], sorted(list(r[0])), sorted(list(r[1]))), reverse=True)
        output_lines = [f'{"/".join(sorted(list(r[0])))} ==> {"/".join(sorted(list(r[1])))},{round(r[2], 2)}\n' for r in rules]
        return output_lines


def load_ibm_data(filename):
    """Getting kaggle data from `dataset/ibm.data`."""

    with open(filename, "r") as fo:
        lines = fo.readlines()
        ibm_data = [
            [token for token in line.strip().split(" ") if token]
            for line in lines
        ]

        data_dict = {}
        for tx in ibm_data:
            if tx[0] in data_dict:
                data_dict[tx[0]].append(tx[2])
            else:
                data_dict[tx[0]] = [tx[2]]

        data = [value for value in data_dict.values()]

        return data

if __name__ == "__main__":
    # create argument for weka
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--algorithm", required=True)
    ap.add_argument("-s", "--minsup", required=True)
    ap.add_argument("-c", "--minconf", required=True)
    args = vars(ap.parse_args())

    # Determine user's algorithm decision
    if args["algorithm"] == "A":
        algorithm = Apriori()
    elif args["algorithm"] == "F":
        algorithm = FPGrowth()

    for i in range(3):
        for j in range(4):
            filename = f"analysis_data/output{i+1}{j+1}.data"
            data = load_ibm_data(filename)
            output, elapsed_time = Associator().generate_rules(algorithm, data, float(args["minsup"]), float(args["minconf"]))
            with open(f"analysis_data/{i+1}{j+1}_{algorithm.__class__.__name__}.csv", "w") as fw:
                fw.writelines(output)
                fw.close()
            print(i+1, j+1, elapsed_time)
