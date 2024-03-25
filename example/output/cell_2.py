# FETCH CODE START
submission = rh.fetchVarResult('submission', varAncestorCell=1, host='results-hub-service.default.svc.cluster.local')
data = rh.fetchVarResult('data', varAncestorCell=1, host='results-hub-service.default.svc.cluster.local')
# FETCH CODE END


from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt

#read and process
iris_data = pd.read_csv(StringIO(data))

iris_data = iris_data.dropna()


print(iris_data.describe())




# SUBMIT CODE START
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=2, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.addVar('data', locals().get('data', None))
submission.submit()
print('Submission Success for cell 2.')
# SUBMIT CODE END

