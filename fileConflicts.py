import json
import os

def read_config_and_get_files_rw(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        return data['filesReadWrite']

def build_conflict_map(output_dir, files_rw):
    txn_operations = {}
    conflicts = {}
    
    # Initialize conflicts for each transaction starting with index 1
    for index in range(1, len(files_rw) + 1):
        conflicts[index] = []
    
    # Parse each transaction and store read and write operations, starting index 1
    for index, access in enumerate(files_rw, start=1):
        operations = access.split()
        txn_operations[index] = {}
        for operation in operations:
            if operation:
                mode, file = operation.split(':')
                if file not in txn_operations[index]:
                    txn_operations[index][file] = set()
                txn_operations[index][file].add(mode)
    
    # Build conflict graph starting with index 1
    for i in range(1, len(files_rw) + 1):
        for j in range(i + 1, len(files_rw) + 1):
            conflict = False
            # Check for conflicts between Txn i and Txn j
            files_i = txn_operations[i].keys()
            files_j = txn_operations[j].keys()
            for file in files_i:
                if file in files_j:
                    modes_i = txn_operations[i][file]
                    modes_j = txn_operations[j][file]
                    # Determine if there's a conflict
                    if ('W' in modes_i or 'W' in modes_j) and not (modes_i == {'R'} and modes_j == {'R'}):
                        conflict = True
                        break
            if conflict:
                conflicts[j].append(i)
    # dump the results into a file
    with open(os.path.join(output_dir, "conflict_list.json"), 'w') as f:
        json.dump(conflicts, f)
    return conflicts

def main():
    files_rw = read_config_and_get_files_rw("J2K_CONFIG.json")
    
    dependency_map = build_conflict_map(files_rw, ".")
    print("Transaction dependencies:")
    for txn, deps in dependency_map.items():
        print(f"Transaction {txn} must wait for: {deps}")

if __name__ == "__main__":
    main()
