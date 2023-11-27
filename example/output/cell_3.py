import matplotlib.pyplot as plt
from io import StringIO
import pandas as pd

# visualization
plt.scatter(iris_data['petal_length'], iris_data['petal_width'])
plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.title('Iris Petal Length vs Width')
plt.show()