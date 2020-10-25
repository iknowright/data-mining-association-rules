class Apriori():
    def __init__(self):
        pass

    '''建立集合C1即對dataSet去重排序'''
    def _createC1(self, dataSet):
        C1 = []
        for transaction in dataSet:
            for item in transaction:
                if not [item] in C1:
                    C1.append([item])
        C1.sort()
        # frozenset表示凍結的set 集合，元素無改變把它當字典的 key 來使用
        return C1
        # return map(frozenset, C1)


    ''' 計算候選資料集CK在資料集D中的支援度，返回大於最小支援度的資料'''
    def _scanD(self, D,Ck,minSupport):
        # ssCnt 臨時存放所有候選項集和頻率.
        ssCnt = {}
        for tid in D:
            # print('1:',tid)
            for can in map(frozenset,Ck):      #每個候選項集can
                # print('2:',can.issubset(tid),can,tid)
                if can.issubset(tid):
                    if not can in ssCnt:
                        ssCnt[can] = 1
                    else:
                        ssCnt[can] +=1

        numItems = float(len(D)) # 所有項集數目
        # 滿足最小支援度的頻繁項集
        retList  = []
        # 滿足最小支援度的頻繁項集和頻率
        supportData = {}

        for key in ssCnt:
            support = ssCnt[key]/numItems   #除以總的記錄條數，即為其支援度
            if support >= minSupport:
                retList.insert(0,key)       #超過最小支援度的項集，將其記錄下來。
            supportData[key] = support
        return retList, supportData


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


    '''找出資料集中支援度不小於最小支援度的候選項集以及它們的支援度即頻繁項集。
    演算法思想：首先構建集合C1，然後掃描資料集來判斷這些只有一個元素的項集是否滿足最小支援度。滿足最小支援度要求的項集構成集合L1。然後L1 中的元素相互組合成C2，C2再進一步過濾變成L2，以此類推，直到C_n的長度為0時結束，即可找出所有頻繁項集的支援度。
    返回：L 頻繁項集的全集
        supportData 所有元素和支援度的全集
    '''
    def _apriori(self, dataSet, minSupport):
        # C1即對dataSet去重排序，然後轉換所有的元素為frozenset
        C1 = self._createC1(dataSet)
        # print(C1)
        # 對每一行進行 set 轉換，然後存放到集合中
        D = list(map(set, dataSet))
        # 計算候選資料集C1在資料集D中的支援度，並返回支援度大於minSupport 的資料
        L1, supportData = self._scanD(D, C1, minSupport)
        # L 加了一層 list, L一共 2 層 list
        L = [L1];k = 2
        # 判斷L第k-2項的資料長度是否>0即頻繁項集第一項。第一次執行時 L 為 [[frozenset([1]), frozenset([3]), frozenset([2]), frozenset([5])]]。L[k-2]=L[0]=[frozenset([1]), frozenset([3]), frozenset([2]), frozenset([5])]，最後面 k += 1
        while (len(L[k-2]) > 0):
            Ck = self._aprioriGen(L[k-2], k) # 例如: 以 {0},{1},{2} 為輸入且 k = 2 則輸出 {0,1}, {0,2}, {1,2}. 以 {0,1},{0,2},{1,2} 為輸入且 k = 3 則輸出 {0,1,2}

            # 返回候選資料集CK在資料集D中的支援度大於最小支援度的資料
            Lk, supK = self._scanD(D, Ck, minSupport)
            # 儲存所有候選項集的支援度，如果字典沒有就追加元素，如果有就更新元素
            supportData.update(supK)
            if len(Lk) == 0:
                break
            # Lk 表示滿足頻繁子項的集合，L 元素在增加，例如:
            # l=[[set(1), set(2), set(3)]]
            # l=[[set(1), set(2), set(3)], [set(1, 2), set(2, 3)]]
            L.append(Lk)
            k += 1
        return L, supportData


    def generateFrequentSet(self, data, minsup):
        # Apriori 演算法生成頻繁項集以及它們的支援度
        L1, supportData1 = self._apriori(data, minSupport=minsup)
        freqSet = []
        for l in L1:
            for i in l:
                freqSet.append(i)

        return freqSet, supportData1
