iris_data = rh.fetchVarResult('iris_data', varAncestorCell=2, host='results-hub-service.default.svc.cluster.local')
submission = rh.fetchVarResult('submission', varAncestorCell=3, host='results-hub-service.default.svc.cluster.local')
import matplotlib.pyplot as plt
from io import StringIO
import pandas as pd


import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=9, host='results-hub-service.default.svc.cluster.local')
submission.submit()
print(f'Submission Success for cell {cell_number}.')

# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=9, host='results-hub-service.default.svc.cluster.local')
submission.addVar('iris_data', locals().get('iris_data', None))
submission.submit()
print(f'Submission Success for cell {cell_number}.')
