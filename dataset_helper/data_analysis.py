def load_data():
    with open("dataset/kaggle.csv", "r") as fo:
        lines = fo.readlines()
        data = [line.strip().split(",") for line in lines]
        return data

def find_unique(data):
    items = set()
    for itemset in data:
        items = set.union(items, itemset)
    items = list(items)
    items.sort()
    return items

def market_basket_optimization():
    data = load_data()
    data_len = len(data)
    print(data_len)
    items = find_unique(data)
    print(len(items))
    average_items_in_set = round(sum([len(itemset) for itemset in data]) / data_len, 2)
    print(average_items_in_set)


if __name__ == "__main__":
    market_basket_optimization()