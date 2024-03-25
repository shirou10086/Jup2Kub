data = rh.fetchVarResult('data', varAncestorCell=10, host='results-hub-service.default.svc.cluster.local')
iris_data = rh.fetchVarResult('iris_data', varAncestorCell=11, host='results-hub-service.default.svc.cluster.local')
submission = rh.fetchVarResult('submission', varAncestorCell=3, host='results-hub-service.default.svc.cluster.local')
import matplotlib.pyplot as plt
from io import StringIO
import pandas as pd

# visualization
plt.scatter(iris_data['petal_length'], iris_data['petal_width'])
plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.title('Iris Petal Length vs Width')
plt.show()
# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=12, host='results-hub-service.default.svc.cluster.local')
submission.submit()
print(f'Submission Success for cell {cell_number}.')

# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=12, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.addVar('data', locals().get('data', None))
submission.submit()
print(f'Submission Success for cell {cell_number}.')
