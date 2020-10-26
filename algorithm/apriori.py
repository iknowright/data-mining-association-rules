class Apriori():
    def __init__(self):
        pass

    def _create_candidate1(self, data):
        '''Find unique items from dataset '''
        initial_candidate = []
        print(data)
        for transaction in data:
            for item in transaction:
                if not [item] in initial_candidate:
                    initial_candidate.append([item])
        initial_candidate.sort()
        return initial_candidate


    def _scanD(self, data, candidate_k, minsup):
        ''' 計算候選資料集 candidate_k 在資料集data中的支援度，返回大於最小支援度的資料'''
        # support_count 臨時存放所有候選項集和頻率.
        support_count = {}
        for transaction in data:
            for candidate in map(frozenset, candidate_k):  #每個候選項集can
                if candidate.issubset(transaction):
                    if not candidate in support_count:
                        support_count[candidate] = 1
                    else:
                        support_count[candidate] +=1

        total_txs = len(data) # 所有項集數目
        # 滿足最小支援度的頻繁項集
        frequent_set  = []
        # 滿足最小支援度的頻繁項集和頻率
        itemset_support = {}

        for key in support_count:
            support = float(support_count[key] / total_txs)   #除以總的記錄條數，即為其支援度
            if support >= minsup:
                frequent_set.insert(0, key)       #超過最小支援度的項集，將其記錄下來。
            itemset_support[key] = support
        return frequent_set, itemset_support


    ''' Apriori演算法：輸入頻繁項集列表Lk，輸出所有可能的候選項集 candidate_k'''
    def _aprioriGen(self, frequent_set, k):
        new_candidate_k = [] # 滿足條件的頻繁項集
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


    '''找出資料集中支援度不小於最小支援度的候選項集以及它們的支援度即頻繁項集。
    演算法思想：首先構建集合C1，然後掃描資料集來判斷這些只有一個元素的項集是否滿足最小支援度。滿足最小支援度要求的項集構成集合L1。然後L1 中的元素相互組合成C2，C2再進一步過濾變成L2，以此類推，直到C_n的長度為0時結束，即可找出所有頻繁項集的支援度。
    返回：L 頻繁項集的全集
        supportData 所有元素和支援度的全集
    '''
    def _apriori(self, data, minsup):
        # candidate_1 即對 data 去重排序，然後轉換所有的元素為frozenset
        candidate_1 = self._create_candidate1(data)

        # 對每一行進行 set 轉換，然後存放到集合中
        data_set = list(map(set, data))

        # 計算候選資料集candidate_1 在資料集 data_set 中的支援度，並返回支援度大於 minsup 的資料
        frequent_set, itemset_support = self._scanD(data_set, candidate_1, minsup)

        # total_frequent_set 加了一層 list, total_frequent_set 一共 2 層 list
        total_frequent_set = [frequent_set]
        k = 2
        # 判斷L第k-2項的資料長度是否>0即頻繁項集第一項。第一次執行時 total_frequent_set 為 [[frozenset([1]), frozenset([3]), frozenset([2]), frozenset([5])]]。L[k-2]=total_frequent_set[0]=[frozenset([1]), frozenset([3]), frozenset([2]), frozenset([5])]，最後面 k += 1
        while (len(total_frequent_set[k-2]) > 0):
            candidate_k = self._aprioriGen(total_frequent_set[k-2], k) # 例如: 以 {0},{1},{2} 為輸入且 k = 2 則輸出 {0,1}, {0,2}, {1,2}. 以 {0,1},{0,2},{1,2} 為輸入且 k = 3 則輸出 {0,1,2}

            # 返回候選資料集candidate在資料集D中的支援度大於最小支援度的資料_k
            k_frequent_set, k_itemset_support = self._scanD(data_set, candidate_k, minsup)
            # 儲存所有候選項集的支援度，如果字典沒有就追加元素，如果有就更新元素
            itemset_support.update(k_itemset_support)
            if len(k_frequent_set) == 0:
                break

            total_frequent_set.append(k_frequent_set)
            k += 1
        return total_frequent_set, itemset_support


    def generateFrequentSet(self, data, minsup):
        total_frequent_set_in_chunk, itemset_support = self._apriori(data, minsup=minsup)
        total_frequent_set = []
        for frequent_set in total_frequent_set_in_chunk:
            for itemset in frequent_set:
                total_frequent_set.append(itemset)

        return total_frequent_set, itemset_support
