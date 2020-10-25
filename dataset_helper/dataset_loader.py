class DataLoader():
    def __init__(self):
        super().__init__()

    @staticmethod
    def load_test_data():
        """
        Load simple test data.

        return `[['A', 'C', 'D'], ['B', 'C', 'E'], ['A', 'B', 'C', 'E'], ['B', 'E']]`
        """

        return [['A', 'C', 'D'], ['B', 'C', 'E'], ['A', 'B', 'C', 'E'], ['B', 'E']]

    @staticmethod
    def load_kaggle_data():
        """Getting kaggle data from `dataset/kaggle.csv`."""

        with open("dataset/kaggle.csv", "r") as fo:
            lines = fo.readlines()
            data = [line.strip().split(",") for line in lines]
            return data

    @staticmethod
    def load_ibm_data():
        """Getting kaggle data from `dataset/ibm.data`."""

        with open("dataset/ibm.data", "r") as fo:
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
