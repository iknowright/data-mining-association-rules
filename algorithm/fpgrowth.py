class TreeNode:
    def __init__(self, name_value, num_occur, parent):
        self.name = name_value
        self.count = num_occur
        self.next_node = None
        self.parent = parent
        self.children = {}

    def increase(self, num_occur):
        self.count += num_occur

    def display(self, ind=1):
        print ('  '*ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.display(ind+1)

class FPGrowth():
    def __init__(self):
        pass

    def _create_FP_tree(self, data, minsup):
        header_table = {}
        for transaction in data:
            for item in transaction:
                header_table[item] = header_table.get(item, 0) + data[transaction]
        keys = [k for k in header_table.keys()]
        for k in keys:
            if header_table[k] < minsup:
                del(header_table[k])

        frequent_itemset = set(header_table.keys())
        if len(frequent_itemset) == 0:
            return None, None
        for k in header_table:
            header_table[k] = [header_table[k], None]

        return_tree = TreeNode('Null Set', 1, None)
        for itemset, count in data.items():
            local_items_count = {}
            for item in itemset:
                if item in frequent_itemset:
                    local_items_count[item] = header_table[item][0]
            if len(local_items_count) > 0:
                ordered_items = [v[0] for v in sorted(local_items_count.items(), key=lambda p:p[1], reverse=True)]
                self._update_FP_tree(ordered_items, return_tree, header_table, count)
        return return_tree, header_table

    def _update_header(self, item_node, targetNode):
        """Determine how many leaves are there for a given item in the tree"""
        # traverse through the next node
        while item_node.next_node != None:
            item_node = item_node.next_node
        item_node.next_node = targetNode

    def _update_FP_tree(self, items, curr_tree, header_table, count):
        # check if current items head is already a curr tree's child
        if items[0] in curr_tree.children:
            curr_tree.children[items[0]].increase(count)
        else:
            # if not, make the item[0] curr tree's child
            curr_tree.children[items[0]] = TreeNode(items[0], count, curr_tree)
            if header_table[items[0]][1] == None:
                header_table[items[0]][1] = curr_tree.children[items[0]]
            else:
                # tells tree there are more than 1 leaf for the given `item` in header_table
                self._update_header(header_table[items[0]][1], curr_tree.children[items[0]])

        # if items are more than 1 then do it recursively, [(0),1,2] --> [(1),2] -> [(2)]
        if len(items) > 1:
            self._update_FP_tree(items[1::], curr_tree.children[items[0]], header_table, count)

    def _ascend_FP_tree(self, curr_node, prefix_path):
        if curr_node.parent != None:
            prefix_path.append(curr_node.name)
            self._ascend_FP_tree(curr_node.parent, prefix_path)

    def _find_prefix_path(self, curr_base_pattern, header_table):
        self_tree = header_table[curr_base_pattern][1]
        condition_patterns = {}
        while self_tree != None:
            prefix_path = []
            self._ascend_FP_tree(self_tree, prefix_path)
            if len(prefix_path) > 1:
                condition_patterns[frozenset(prefix_path[1:])] = self_tree.count
            self_tree = self_tree.next_node
        return condition_patterns

    def _mine_FP_tree(self, curr_tree, header_table, minsup, prefix, total_frequent_set, itemset_support):
        try:
            reverse_items = [v[0] for v in sorted(header_table.items(), key=lambda p:p[1][0])]
            for curr_base_pattern in reverse_items:
                new_frequent_itemset = prefix.copy()
                new_frequent_itemset.add(curr_base_pattern)

                total_frequent_set.append(frozenset(new_frequent_itemset))

                itemset_support[frozenset(new_frequent_itemset)] = header_table[curr_base_pattern][0]

                # print(f"curr:{curr_base_pattern}, prefix: {prefix if prefix else '{}'}, freqset: {new_frequent_itemset}, support: {header_table[curr_base_pattern][0]}")

                condition_pattern_base = self._find_prefix_path(curr_base_pattern, header_table)

                sub_tree, sub_header_table = self._create_FP_tree(condition_pattern_base, minsup)
                if sub_header_table != None:
                    sub_tree.display()
                    print()
                    self._mine_FP_tree(sub_tree, sub_header_table, minsup, new_frequent_itemset, total_frequent_set, itemset_support)
        except:
            pass

    def _create_init_set(self, data):
        """Return {itemset: count, ...}"""

        itemset_count = {}
        for transaction in data:
            if frozenset(transaction) in itemset_count:
                itemset_count[frozenset(transaction)] += 1
            else:
                itemset_count[frozenset(transaction)] = 1
        return itemset_count


    def generateFrequentSet(self, data, minsup):
        minsup_index = minsup * len(data)

        init_set = self._create_init_set(data)
        fp_tree, header_table = self._create_FP_tree(init_set, minsup_index)
        fp_tree.display()
        print()

        frequent_set = []
        itemset_support = {}

        self._mine_FP_tree(fp_tree, header_table, minsup_index, set(), frequent_set, itemset_support)

        if frequent_set:
            for k, v in itemset_support.items():
                itemset_support[k] = round(v / len(data), 2)

        return frequent_set, itemset_support
