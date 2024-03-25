# FETCH CODE START
data = rh.fetchVarResult('data', varAncestorCell=1, host='results-hub-service.default.svc.cluster.local')
iris_data = rh.fetchVarResult('iris_data', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
# FETCH CODE END

import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# visualization
plt.scatter(iris_data['petal_length'], iris_data['petal_width'])
plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.title('Iris Petal Length vs Width')
plt.show()

# SUBMIT CODE START
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=3, host='results-hub-service.default.svc.cluster.local')
submission.submit()
print('Submission Success for cell 3.')
# SUBMIT CODE END
