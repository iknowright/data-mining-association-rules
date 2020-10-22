import weka.core.jvm as jvm
from weka.associations import Associator
from weka.core.converters import Loader
jvm.start()

loader = Loader(classname="weka.core.converters.ArffLoader")
data = loader.load_file("sample.arff")
print(data)

associator = Associator(classname="weka.associations.Apriori", options=["-M", "0.5", "-C", "0.5", "-N", "100"])
associator.build_associations(data)

print(associator)

jvm.stop()
