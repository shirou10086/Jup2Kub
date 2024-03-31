# FETCH CODE START
import ResultsHub as rh
filename = rh.fetchVarResult('filename', varAncestorCell=1, host='results-hub-service.default.svc.cluster.local')
content = rh.fetchVarResult('content', varAncestorCell=1, host='results-hub-service.default.svc.cluster.local')
# FETCH CODE END

# Part 2: Listing all files in the current directory
import os

print("\nFiles in the current directory:")
for file in os.listdir('.'):
    print(file)

# SUBMIT CODE START
submission = rh.ResultsHubSubmission(cell_number=2, host='results-hub-service.default.svc.cluster.local')
submission.addVar('file', locals().get('file', None))
submission.submit()
print('Submission Success for cell 2.')
# SUBMIT CODE END
