import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO


import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Upload tracked variables to ResultsHub
import ResultsHub as rh
submission = rh.ResultsHubSubmission(cell_number=0, host='results-hub-service.default.svc.cluster.local')
submission.submit()
print(f'Submission Success for cell {cell_number}.')
