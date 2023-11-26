import pandas as pd
import matplotlib.pyplot as plt


iris_data = pd.read_csv('iris.csv')

# Data preprocessing: remove missing or null values
iris_data = iris_data.dropna()

# Data exploration: get basic statistics about the data
print(iris_data.describe())

# Data visualization: plot petal length against petal width
plt.scatter(iris_data['petal_length'], iris_data['petal_width'])
plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.title('Iris Petal Length vs Width')
plt.show()
