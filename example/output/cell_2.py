import matplotlib.pyplot as plt
from io import StringIO
import pandas as pd

#read and process
iris_data = pd.read_csv(StringIO(data))

iris_data = iris_data.dropna()


print(iris_data.describe())

