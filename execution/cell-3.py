# FETCH CODE START
import ResultsHub as rh
data = rh.fetchVarResult('data', varAncestorCell=1, host='results-hub-service.default.svc.cluster.local')
iris_data = rh.fetchVarResult('iris_data', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
# FETCH CODE END

import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt

# visualization
plt.scatter(iris_data['petal_length'], iris_data['petal_width'])
plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.title('Iris Petal Length vs Width')
plt.show()

# SUBMIT CODE START
submission = rh.ResultsHubSubmission(cell_number=3, host='results-hub-service.default.svc.cluster.local')
submission.submit()
print('Submission Success for cell 3.')
# SUBMIT CODE END
