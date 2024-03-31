# FETCH CODE START
import ResultsHub as rh
# FETCH CODE END


import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO


# SUBMIT CODE START
submission = rh.ResultsHubSubmission(cell_number=1, host='results-hub-service.default.svc.cluster.local')
submission.submit()
print('Submission Success for cell 1.')
# SUBMIT CODE END
