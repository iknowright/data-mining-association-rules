import argparse
import time

from algorithm.apriori import Apriori
from algorithm.fpgrowth import FPGrowth
from dataset_helper.dataset_loader import DataLoader


def execution_timer(func):
    """
    timer for execution
    """

    def wrapper(*args):
        start = time.time()
        func_ret = func(*args)
        elapsed = time.time() - start
        print(f'{func.__name__}:time {elapsed} elapsed second(s)')
        return func_ret, elapsed
    return wrapper


class Associator():
    def __init__(self):
        pass

    ''' Apriori演算法：輸入頻繁項集列表Lk，輸出所有可能的候選項集 Ck'''
    def _aprioriGen(self, Lk, k):
        retList = [] # 滿足條件的頻繁項集
        lenLk = len(Lk)
        for i in range(lenLk):
            for j in range(i+1, lenLk):
                L1 = list(Lk[i])[: k-2]
                L2 = list(Lk[j])[: k-2]
                # print '-----i=', i, k-2, Lk, Lk[i], list(Lk[i])[: k-2]
                # print '-----j=', j, k-2, Lk, Lk[j], list(Lk[j])[: k-2]
                L1.sort()
                L2.sort()
                if L1 == L2:
                    retList.append(Lk[i] | Lk[j])
        return retList


    '''計算可信度（confidence）
    Args:
        freqSet 頻繁項集中的元素，例如: frozenset([1, 3])
        H 頻繁項集中的元素的集合，例如: [frozenset([1]), frozenset([3])]
        supportData 所有元素的支援度的字典
        brl 關聯規則列表的空陣列
        minConf 最小可信度
    Returns:
        prunedH 記錄 可信度大於閾值的集合
    '''
    def _calcConf(self, freqSet, H, supportData, brl, minConf):
        # 記錄可信度大於最小可信度（minConf）的集合
        prunedH = []
        for conseq in H: # 假設 freqSet = frozenset([1, 3]), H = [frozenset([1]), frozenset([3])]，那麼現在需要求出 frozenset([1]) -> frozenset([3]) 的可信度和 frozenset([3]) -> frozenset([1]) 的可信度
            try:
                conf = supportData[freqSet]/supportData[freqSet-conseq] # 支援度定義: a -> b = support(a | b) / support(a). 假設  freqSet = frozenset([1, 3]), conseq = [frozenset([1])]，那麼 frozenset([1]) 至 frozenset([3]) 的可信度為 = support(a | b) / support(a) = supportData[freqSet]/supportData[freqSet-conseq] = supportData[frozenset([1, 3])] / supportData[frozenset([1])]
                if conf >= minConf:
                    # 只要買了 freqSet-conseq 集合，一定會買 conseq 集合（freqSet-conseq 集合和 conseq集合 是全集）
                    print (freqSet-conseq, '-->', conseq, 'conf:', conf)
                    brl.append((freqSet-conseq, conseq, conf))
                    prunedH.append(conseq)
            except:
                pass
        return prunedH


    """遞迴計算頻繁項集的規則
        Args:
            freqSet 頻繁項集中的元素，例如: frozenset([2, 3, 5])
            H 頻繁項集中的元素的集合，例如: [frozenset([2]), frozenset([3]), frozenset([5])]
            supportData 所有元素的支援度的字典
            brl 關聯規則列表的陣列
            minConf 最小可信度
    """
    def _rulesFromConseq(self, freqSet, H, supportData, brl, minConf):
        # H[0] 是 freqSet 的元素組合的第一個元素，並且 H 中所有元素的長度都一樣，長度由 _aprioriGen(H, m+1) 這裡的 m + 1 來控制
        # 該函式遞迴時，H[0] 的長度從 1 開始增長 1 2 3 ...
        # 假設 freqSet = frozenset([2, 3, 5]), H = [frozenset([2]), frozenset([3]), frozenset([5])]
        # 那麼 m = len(H[0]) 的遞迴的值依次為 1 2
        # 在 m = 2 時, 跳出該遞迴。假設再遞迴一次，那麼 H[0] = frozenset([2, 3, 5])，freqSet = frozenset([2, 3, 5]) ，沒必要再計算 freqSet 與 H[0] 的關聯規則了。
        m = len(H[0])
        if (len(freqSet) > (m + 1)):
            # 生成 m+1 個長度的所有可能的 H 中的組合，假設 H = [frozenset([2]), frozenset([3]), frozenset([5])]
            # 第一次遞迴呼叫時生成 [frozenset([2, 3]), frozenset([2, 5]), frozenset([3, 5])]
            # 第二次 。。。沒有第二次，遞迴條件判斷時已經退出了
            Hmp1 = self._aprioriGen(H, m+1)
            # 返回可信度大於最小可信度的集合
            Hmp1 = self._calcConf(freqSet, Hmp1, supportData, brl, minConf)
            # print ('Hmp1=', Hmp1)
            # print ('len(Hmp1)=', len(Hmp1), 'len(freqSet)=', len(freqSet))
            # 計算可信度後，還有資料大於最小可信度的話，那麼繼續遞迴呼叫，否則跳出遞迴
            if (len(Hmp1) > 1):
                # print '----------------------', Hmp1
                # print len(freqSet),  len(Hmp1[0]) + 1
                self._rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)


    '''生成關聯規則
        Args:
            L 頻繁項集列表
            supportData 頻繁項集支援度的字典
            minConf 最小置信度
        Returns:
            bigRuleList 可信度規則列表（關於 (A->B+置信度) 3個欄位的組合）
    '''
    def _generateRules(self, L, supportData, minConf):
        bigRuleList = []
        for freqSet in L:
        # 組合總的元素並遍歷子元素，轉化為 frozenset集合存放到 list 列表中
            H1 = [frozenset([item]) for item in freqSet]
            # 2 個的組合else, 2 個以上的組合 if
            if (len(freqSet) > 2):
                self._rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            elif len(freqSet) == 2:
                self._calcConf(freqSet, H1, supportData, bigRuleList, minConf)
        return bigRuleList


    @execution_timer
    def generate_rules(self, algorithm, data, minsup, minconf):
        print(algorithm)
        L1, supportData1 = algorithm.generateFrequentSet(data, minsup)

        # 生成關聯規則
        rules = self._generateRules(L1, supportData1, minConf=minconf)
        # print ('rules: ', rules)
        rules.sort(key=lambda r: (r[2], sorted(list(r[0])), sorted(list(r[1]))), reverse=True)
        output_lines = [f'{"/".join(sorted(list(r[0])))} ==> {"/".join(sorted(list(r[1])))},{round(r[2], 2)}\n' for r in rules]
        return output_lines


if __name__ == "__main__":
    # create argument for weka
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--algorithm", required=True)
    ap.add_argument("-t", "--type", required=True)
    ap.add_argument("-s", "--minsup", required=True)
    ap.add_argument("-c", "--minconf", required=True)
    args = vars(ap.parse_args())

    # Determine dataset
    if args["type"] == "kaggle":
        data = DataLoader.load_kaggle_data()
    elif args["type"] == "sample":
        data = DataLoader.load_test_data()
    elif args["type"] == "ibm":
        data = DataLoader.load_ibm_data()

    # Determine user's algorithm decision
    if args["algorithm"] == "A":
        algorithm = Apriori()
    elif args["algorithm"] == "F":
        algorithm = FPGrowth()

    output, _ = Associator().generate_rules(algorithm, data, float(args["minsup"]), float(args["minconf"]))
    with open(f"results/{args['type']}_{algorithm.__class__.__name__}.csv", "w") as fw:
        fw.writelines(output)
        fw.close()