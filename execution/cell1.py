# FETCH CODE START
import ResultsHub as rh
# FETCH CODE END

import os

# Part 1: Reading a text file
filename = 'example.txt'  # Assuming the file is named example.txt
with open(filename, 'r') as file:
    content = file.read()
    print("Content of example.txt:")
    print(content)




# SUBMIT CODE START
submission = rh.ResultsHubSubmission(cell_number=1, host='results-hub-service.default.svc.cluster.local')
submission.addVar('filename', locals().get('filename', None))
submission.addVar('content', locals().get('content', None))
submission.submit()
print('Submission Success for cell 1.')
# SUBMIT CODE END
