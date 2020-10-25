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

class FPGrowth():
    def __init__(self):
        pass

    def _createFPtree(self, dataSet, minSup=1):
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
                self._updateFPtree(orderedItem, retTree, headerTable, count)
        return retTree, headerTable


    def _updateHeader(self, nodeToTest, targetNode):
        while nodeToTest.nodeLink != None:
            nodeToTest = nodeToTest.nodeLink
        nodeToTest.nodeLink = targetNode


    def _updateFPtree(self, items, inTree, headerTable, count):
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
                self._updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
        # 递归
        if len(items) > 1:
            self._updateFPtree(items[1::], inTree.children[items[0]], headerTable, count)

    # 递归回溯
    def _ascendFPtree(self, leafNode, prefixPath):
        if leafNode.parent != None:
            prefixPath.append(leafNode.name)
            self._ascendFPtree(leafNode.parent, prefixPath)
    # 条件模式基


    def _findPrefixPath(self, basePat, myHeaderTab):
        treeNode = myHeaderTab[basePat][1] # basePat在FP树中的第一个结点
        condPats = {}
        while treeNode != None:
            prefixPath = []
            self._ascendFPtree(treeNode, prefixPath) # prefixPath是倒过来的，从treeNode开始到根
            if len(prefixPath) > 1:
                condPats[frozenset(prefixPath[1:])] = treeNode.count # 关联treeNode的计数
            treeNode = treeNode.nodeLink # 下一个basePat结点
        return condPats


    def _mineFPtree(self, inTree, headerTable, minSup, preFix, freqItemList, supportData):
        # 最开始的频繁项集是headerTable中的各元素
        bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p:p[1][0])] # 根据频繁项的总频次排序
        for basePat in bigL: # 对每个频繁项
            newFreqSet = preFix.copy()
            newFreqSet.add(basePat)
            freqItemList.append(frozenset(newFreqSet))
            supportData[frozenset(newFreqSet)] = headerTable[basePat][0]
            condPattBases = self._findPrefixPath(basePat, headerTable) # 当前频繁项集的条件模式基
            myCondTree, myHead = self._createFPtree(condPattBases, minSup) # 构造当前频繁项的条件FP树
            if myHead != None:
                # print 'conditional tree for: ', newFreqSet
                # myCondTree.disp(1)
                self._mineFPtree(myCondTree, myHead, minSup, newFreqSet, freqItemList, supportData) # 递归挖掘条件FP树

    def _createInitSet(self, dataSet):
        retDict={}
        for trans in dataSet:
            key = frozenset(trans)
            if key in retDict:
                retDict[frozenset(trans)] += 1
            else:
                retDict[frozenset(trans)] = 1
        return retDict


    def generateFrequentSet(self, data, minsup):
        minsup_index = minsup * len(data)

        initSet = self._createInitSet(data)
        myFPtree, myHeaderTab = self._createFPtree(initSet, minsup_index)

        freqItems = []
        supportData = {}
        self._mineFPtree(myFPtree, myHeaderTab, minsup_index, set([]), freqItems, supportData)

        for k, v in supportData.items():
            supportData[k] = round(v / len(data), 2)

        return freqItems, supportData
