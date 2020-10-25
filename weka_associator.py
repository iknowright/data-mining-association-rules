import argparse
import time

import weka.core.jvm as jvm
from weka.associations import Associator
from weka.core.converters import Loader


def execution_timer(func):
    """
    timer for execution
    """

    def wrapper(*args):
        start = time.time()
        func_ret = func(*args)
        elapsed = time.time() - start
        print(f'{func.__name__}:time {elapsed} elapsed second(s)')
        return func_ret
    return wrapper


@execution_timer
def weka_algorithm(algorithm, type, minsup, minconf):
    # Weka worker start
    jvm.start()

    loader = Loader(classname="weka.core.converters.ArffLoader")
    data = loader.load_file(arr_file)

    associator = Associator(
        classname=f"weka.associations.{algorithm}",
        options=["-M", minsup, "-C", minconf, "-N", "100"]
    )
    associator.build_associations(data)

    with open(f"results/{type}_weka_{algorithm}.output","w") as fw:
        fw.write(associator.__str__())
        fw.close()

    # Weka worker end
    jvm.stop()


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
        arr_file = "dataset/kaggle.arff"
    elif args["type"] == "sample":
        arr_file = "dataset/sample.arff"
    elif args["type"] == "ibm":
        arr_file = "dataset/ibm.arff"

    # Determine user's algorithm decision
    if args["algorithm"] == "A":
        algorithm = "Apriori"
    elif args["algorithm"] == "F":
        algorithm = "FPGrowth"

    weka_algorithm(algorithm, args["type"], args["minsup"], args["minconf"])
