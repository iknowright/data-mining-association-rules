def loadDataSet():
    return [['A', 'C', 'D'], ['B', 'C', 'E'], ['A', 'B', 'C', 'E'], ['B', 'E']]


class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def increase(self, numOccur):
        self.count += numOccur

    def display(self, ind=1):
        print ('  '*ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.display(ind+1)


def createFPtree(dataSet, minSup=1):
    headerTable = {}
    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    keys = [k for k in headerTable.keys()]
    for k in keys:
        if headerTable[k] < minSup:
            del(headerTable[k]) # 删除不满足最小支持度的元素
    freqItemSet = set(headerTable.keys()) # 满足最小支持度的频繁项集
    if len(freqItemSet) == 0:
        return None, None
    for k in headerTable:
        headerTable[k] = [headerTable[k], None] # element: [count, node]

    retTree = treeNode('Null Set', 1, None)
    for tranSet, count in dataSet.items():
        # dataSet：[element, count]
        localD = {}
        for item in tranSet:
            if item in freqItemSet: # 过滤，只取该样本中满足最小支持度的频繁项
                localD[item] = headerTable[item][0] # element : count
        if len(localD) > 0:
            # 根据全局频数从大到小对单样本排序
            orderedItem = [v[0] for v in sorted(localD.items(), key=lambda p:p[1], reverse=True)]
            # 用过滤且排序后的样本更新树
            updateFPtree(orderedItem, retTree, headerTable, count)
    return retTree, headerTable


def updateHeader(nodeToTest, targetNode):
    while nodeToTest.nodeLink != None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


def updateFPtree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        # 判断items的第一个结点是否已作为子结点
        inTree.children[items[0]].increase(count)
    else:
        # 创建新的分支
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 更新相应频繁项集的链表，往后添加
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    # 递归
    if len(items) > 1:
        updateFPtree(items[1::], inTree.children[items[0]], headerTable, count)



# 递归回溯
def ascendFPtree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendFPtree(leafNode.parent, prefixPath)
# 条件模式基


def findPrefixPath(basePat, myHeaderTab):
    treeNode = myHeaderTab[basePat][1] # basePat在FP树中的第一个结点
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendFPtree(treeNode, prefixPath) # prefixPath是倒过来的，从treeNode开始到根
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count # 关联treeNode的计数
        treeNode = treeNode.nodeLink # 下一个basePat结点
    return condPats


def mineFPtree(inTree, headerTable, minSup, preFix, freqItemList, supportData):
    # 最开始的频繁项集是headerTable中的各元素
    print("======>", headerTable.items())
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p:p[1][0])] # 根据频繁项的总频次排序
    print("======>", bigL)
    for basePat in bigL: # 对每个频繁项
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        freqItemList.append(frozenset(newFreqSet))
        supportData[frozenset(newFreqSet)] = headerTable[basePat][0]
        condPattBases = findPrefixPath(basePat, headerTable) # 当前频繁项集的条件模式基
        print(newFreqSet, condPattBases)
        myCondTree, myHead = createFPtree(condPattBases, minSup) # 构造当前频繁项的条件FP树
        print(myHead)
        if myHead != None:
            # print 'conditional tree for: ', newFreqSet
            # myCondTree.disp(1)
            mineFPtree(myCondTree, myHead, minSup, newFreqSet, freqItemList, supportData) # 递归挖掘条件FP树

def createInitSet(dataSet):
    retDict={}
    for trans in dataSet:
        key = frozenset(trans)
        if key in retDict:
            retDict[frozenset(trans)] += 1
        else:
            retDict[frozenset(trans)] = 1
    return retDict



''' Apriori演算法：輸入頻繁項集列表Lk，輸出所有可能的候選項集 Ck'''
def aprioriGen(Lk, k):
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
def calcConf(freqSet, H, supportData, brl, minConf=0.7):
    # 記錄可信度大於最小可信度（minConf）的集合
    prunedH = []
    for conseq in H: # 假設 freqSet = frozenset([1, 3]), H = [frozenset([1]), frozenset([3])]，那麼現在需要求出 frozenset([1]) -> frozenset([3]) 的可信度和 frozenset([3]) -> frozenset([1]) 的可信度
        conf = supportData[freqSet]/supportData[freqSet-conseq] # 支援度定義: a -> b = support(a | b) / support(a). 假設  freqSet = frozenset([1, 3]), conseq = [frozenset([1])]，那麼 frozenset([1]) 至 frozenset([3]) 的可信度為 = support(a | b) / support(a) = supportData[freqSet]/supportData[freqSet-conseq] = supportData[frozenset([1, 3])] / supportData[frozenset([1])]
        if conf >= minConf:
            # 只要買了 freqSet-conseq 集合，一定會買 conseq 集合（freqSet-conseq 集合和 conseq集合 是全集）
            print (freqSet-conseq, '-->', conseq, 'conf:', conf)
            brl.append((freqSet-conseq, conseq, conf))
            prunedH.append(conseq)
    return prunedH



"""遞迴計算頻繁項集的規則
    Args:
        freqSet 頻繁項集中的元素，例如: frozenset([2, 3, 5])
        H 頻繁項集中的元素的集合，例如: [frozenset([2]), frozenset([3]), frozenset([5])]
        supportData 所有元素的支援度的字典
        brl 關聯規則列表的陣列
        minConf 最小可信度
"""
def rulesFromConseq(freqSet, H, supportData, brl, minConf=0.7):
    # H[0] 是 freqSet 的元素組合的第一個元素，並且 H 中所有元素的長度都一樣，長度由 aprioriGen(H, m+1) 這裡的 m + 1 來控制
    # 該函式遞迴時，H[0] 的長度從 1 開始增長 1 2 3 ...
    # 假設 freqSet = frozenset([2, 3, 5]), H = [frozenset([2]), frozenset([3]), frozenset([5])]
    # 那麼 m = len(H[0]) 的遞迴的值依次為 1 2
    # 在 m = 2 時, 跳出該遞迴。假設再遞迴一次，那麼 H[0] = frozenset([2, 3, 5])，freqSet = frozenset([2, 3, 5]) ，沒必要再計算 freqSet 與 H[0] 的關聯規則了。
    m = len(H[0])
    if (len(freqSet) > (m + 1)):
        # 生成 m+1 個長度的所有可能的 H 中的組合，假設 H = [frozenset([2]), frozenset([3]), frozenset([5])]
        # 第一次遞迴呼叫時生成 [frozenset([2, 3]), frozenset([2, 5]), frozenset([3, 5])]
        # 第二次 。。。沒有第二次，遞迴條件判斷時已經退出了
        Hmp1 = aprioriGen(H, m+1)
        # 返回可信度大於最小可信度的集合
        Hmp1 = calcConf(freqSet, Hmp1, supportData, brl, minConf)
        # print ('Hmp1=', Hmp1)
        # print ('len(Hmp1)=', len(Hmp1), 'len(freqSet)=', len(freqSet))
        # 計算可信度後，還有資料大於最小可信度的話，那麼繼續遞迴呼叫，否則跳出遞迴
        if (len(Hmp1) > 1):
            # print '----------------------', Hmp1
            # print len(freqSet),  len(Hmp1[0]) + 1
            rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)


'''生成關聯規則
    Args:
        L 頻繁項集列表
        supportData 頻繁項集支援度的字典
        minConf 最小置信度
    Returns:
        bigRuleList 可信度規則列表（關於 (A->B+置信度) 3個欄位的組合）
'''
def generateRules(L, supportData, minConf=0.7):
    bigRuleList = []
    # 獲取頻繁項集中每個組合的所有元素
    for freqSet in L:
        # 組合總的元素並遍歷子元素，轉化為 frozenset集合存放到 list 列表中
        H1 = [frozenset([item]) for item in freqSet]
        # print(H1)
        # 2 個的組合else, 2 個以上的組合 if
        if (len(freqSet) > 2):
            rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
        elif len(freqSet) == 2:
            calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList



if __name__ == "__main__":
    simDat = loadDataSet()
    initSet = createInitSet(simDat)
    myFPtree, myHeaderTab = createFPtree(initSet, 2)
    print(myFPtree.display())
    print(myHeaderTab)

    freqItems = []
    supportData = {}
    mineFPtree(myFPtree, myHeaderTab, 2, set([]), freqItems, supportData)
    for x in freqItems:
        print(x)

    for k, v in supportData.items():
        supportData[k] = round(v / len(simDat), 2)
        print(k,supportData[k])

    print()

    # 生成關聯規則
    rules = generateRules(freqItems, supportData, minConf=0.5)
    # print ('rules: ', rules)
    rules.sort(key=lambda r: r[2], reverse=True)
    output_lines = [f'{r.__str__()}\n' for r in rules]
    # print(output_lines)

    print()
    for a,b, conf in rules:
        print(a, '-->', b, 'conf:', conf)

