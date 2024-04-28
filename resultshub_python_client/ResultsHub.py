import grpc
import pickle
import time
import J2kResultsHub_pb2
import J2kResultsHub_pb2_grpc

class ResultsHubSubmission:
    def __init__(self, cell_number, host='localhost'):
        self.cell_number = cell_number
        self.host = host
        self.port = '50051' 
        self.var_results = J2kResultsHub_pb2.VarResults(cellNumber=cell_number)

    def addVar(self, var_name, var):
        var_bytes = pickle.dumps(var)
        var_result = J2kResultsHub_pb2.VarResult(
            varName=var_name, varBytes=var_bytes, available=True, isJson=False
        )
        self.var_results.varResuls.append(var_result)
    
    def addJson(self, json_name, json_string):
        var_result = J2kResultsHub_pb2.VarResult(
            varName=json_name, available=True, isJson=True, jsonString=json_string
        )
        self.var_results.varResults.append(var_result)

    def submit(self):
        # keep retrying until success
        while True:
            try:
                # Use the host attribute
                with grpc.insecure_channel(f'{self.host}:{self.port}') as channel:
                    stub = J2kResultsHub_pb2_grpc.ResultsHubStub(channel)
                    stub.ClaimCellFinished(self.var_results)
                    print("Submission RPC returned successfully.")
                    return
            except grpc.RpcError as e:
                print(f"Submission failed: {e}, retrying...")
                time.sleep(2)  # Wait for 2 seconds before retrying

def fetchVarResult(varName, varAncestorCell, host='localhost'):
    port = '50051'
    while True:
        try:
            with grpc.insecure_channel(f'{host}:{port}') as channel:
                stub = J2kResultsHub_pb2_grpc.ResultsHubStub(channel)
                fetch_request = J2kResultsHub_pb2.FetchVarResultRequest(
                    varName=varName, varAncestorCell=varAncestorCell
                )
                fetched_var = stub.FetchVarResult(fetch_request)
                if not fetched_var.isJson:
                    return pickle.loads(fetched_var.varBytes)
                else:
                    return fetched_var.jsonString
        except grpc.RpcError as e:
            print(f"Fetching var {varName} failed: {e}, retrying in 2 seconds...")
            time.sleep(2)

def waitForCell(waitFor, host='localhost'):
    port = '50051'
    while True:
        try:
            with grpc.insecure_channel(f'{host}:{port}') as channel:
                stub = J2kResultsHub_pb2_grpc.ResultsHubStub(channel)
                wait_Request = J2kResultsHub_pb2.WaitCellRequest(waitFor=waitFor)
                stub.WaitForCell(wait_Request)
                # if rpc returned without error, then we are good
                return
        except grpc.RpcError as e:
            print(f"Waiting for cell{waitFor} errored: {e}, retrying in 2 seconds...")
            time.sleep(2)