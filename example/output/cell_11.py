data = rh.fetchVarResult('data', varAncestorCell=10, host='results-hub-service.default.svc.cluster.local')
submission = rh.fetchVarResult('submission', varAncestorCell=3, host='results-hub-service.default.svc.cluster.local')
import matplotlib.pyplot as plt
from io import StringIO
import pandas as pd

#read and process
iris_data = pd.read_csv(StringIO(data))

iris_data = iris_data.dropna()


print(iris_data.describe())


# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=11, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.submit()
print(f'Submission Success for cell {cell_number}.')

# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=11, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.addVar('data', locals().get('data', None))
submission.submit()
print(f'Submission Success for cell {cell_number}.')
