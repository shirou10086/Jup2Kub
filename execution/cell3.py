# FETCH CODE START
import ResultsHub as rh
data = rh.fetchVarResult('data', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
# FETCH CODE END

import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

#read and process
iris_data = pd.read_csv(StringIO(data))

iris_data = iris_data.dropna()


print(iris_data.describe())



# SUBMIT CODE START
submission = rh.ResultsHubSubmission(cell_number=3, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.submit()
print('Submission Success for cell 3.')
# SUBMIT CODE END
