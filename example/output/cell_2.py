import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt

#read and process
iris_data = pd.read_csv(StringIO(data))

iris_data = iris_data.dropna()


print(iris_data.describe())

