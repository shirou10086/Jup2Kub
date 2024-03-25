iris_data = rh.fetchVarResult('iris_data', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

# visualization
plt.scatter(iris_data['petal_length'], iris_data['petal_width'])
plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.title('Iris Petal Length vs Width')
plt.show()
# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=3, host='results-hub-service.default.svc.cluster.local')
submission.submit()
print(f'Submission Success for cell {cell_number}.')

# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=3, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.submit()
print(f'Submission Success for cell {cell_number}.')
