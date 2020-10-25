def load_data():
    with open("kaggle.csv", "r") as fo:
        lines = fo.readlines()
        data = [set(line.strip().split(",")) for line in lines]
        print(data[:5])
        return data

def find_unique(data):
    items = set()
    for itemset in data:
        items = set.union(items, itemset)
    items = list(items)
    items.sort()
    return items

def generate_row(items, row_itemset):
    row = ""
    for item in items:
        if item in row_itemset:
            row += f"'1',"
        else:
            row += f"?,"
    row = row[:-1]
    return row


def build_relation(relation):
    return f"@relation '{relation}'\n"


def build_attributes(items):
    attributes = ""
    for item in items:
        attributes += f"@attribute '{item}', {{'1'}}\n"
    return attributes


def build_data_rows(items, data):
    data_str = "@data\n"
    for itemset in data:
        data_str += f"{generate_row(items, itemset)}\n"
    return data_str


def generate_ARFF():
    data = load_data()
    items = find_unique(data)

    context = ""
    context += build_relation("goods") + "\n"
    context += build_attributes(items) + "\n"
    context += build_data_rows(items, data) + "\n"

    with open("kaggle.arff", "w") as fw:
        fw.write(context)
        fw.close()


if __name__ == "__main__":
    generate_ARFF()