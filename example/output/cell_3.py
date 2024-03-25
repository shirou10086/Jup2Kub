# FETCH CODE START
submission = rh.fetchVarResult('submission', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
data = rh.fetchVarResult('data', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
iris_data = rh.fetchVarResult('iris_data', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
# FETCH CODE END


from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt

# visualization
plt.scatter(iris_data['petal_length'], iris_data['petal_width'])
plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.title('Iris Petal Length vs Width')
plt.show()


# SUBMIT CODE START
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=3, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.addVar('data', locals().get('data', None))
submission.submit()
print('Submission Success for cell 3.')
# SUBMIT CODE END

