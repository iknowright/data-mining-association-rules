import weka.core.jvm as jvm
from weka.associations import Associator
from weka.core.converters import Loader
jvm.start()

loader = Loader(classname="weka.core.converters.ArffLoader")
data = loader.load_file("dataset/kaggle.arff")

associator = Associator(classname="weka.associations.Apriori", options=["-M", "0.01", "-C", "0.01", "-N", "100"])
associator.build_associations(data)

with open("weka.output","w") as fw:
    fw.write(associator.__str__())
    fw.close()

jvm.stop()
