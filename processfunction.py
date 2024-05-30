import glob
import re
import os

def extract_functions_from_file(file_path):
    """
    Extract function definitions from a file, supporting both R and Python.
    """
    if file_path.endswith('.R'):
        function_pattern = re.compile(r"(\b\w+\s*<- function\(.*?\)\s*\{.*?\n\})", re.DOTALL)
    elif file_path.endswith('.py'):
        function_pattern = re.compile(r"def\s+(\w+)\s*\(.*?\)\s*:", re.DOTALL)
    else:
        return {}  

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        if file_path.endswith('.R'):
            functions = function_pattern.findall(content)
            return {f.split('<-')[0].strip(): f for f in functions}
        elif file_path.endswith('.py'):
            functions = function_pattern.findall(content)
            function_defs = {}
            for func in functions:
                start_index = content.find(f"def {func}")
                end_index = content.find("def ", start_index + 1)
                function_defs[func] = content[start_index:end_index] if end_index != -1 else content[start_index:]
            return function_defs
def prepend_functions_to_subsequent_files(source_functions, all_files, original_file_index):
    """
    Prepend function definitions to subsequent R and Python files in the list.
    For Python files, place them after the first empty line after import.
    For R files, place them after the first '#R' comment line.
    """
    for file_path in all_files[original_file_index+1:]:
        with open(file_path, 'r+', encoding='utf-8') as file:
            content = file.read()
            prepend_content = ''
            insertion_point = 0

            if file_path.endswith('.py'):
                # Determine the first empty line after initial comments or import statements
                first_empty_line_index = content.find('\n\n')
                if first_empty_line_index == -1:
                    first_empty_line_index = 0  # If no empty line found, start at the beginning
                else:
                    first_empty_line_index += 1  # Place after the first empty line
                insertion_point = first_empty_line_index

            elif file_path.endswith('.R'):
                # add after the first '#R' comment
                r_comment_index = content.find('#R')
                if r_comment_index != -1:
                    end_of_line_index = content.find('\n', r_comment_index)
                    if end_of_line_index != -1:
                        insertion_point = end_of_line_index + 1
                else:
                    insertion_point = 0  # If '#R' not found, start at the beginning

            for func_name, func_def in source_functions.items():
                if re.search(r'\b' + re.escape(func_name) + r'\b', content):
                    if (file_path.endswith('.py') and f"def {func_name}" not in content) or \
                       (file_path.endswith('.R') and f"{func_name} <- function" not in content):
                        prepend_content += func_def + '\n\n'

            if prepend_content:
                content = content[:insertion_point] + prepend_content + content[insertion_point:]
                file.seek(0)
                file.write(content)
                file.truncate()
                print(f"Prepended new functions to {file_path} from {all_files[original_file_index]}.")


def process_directory(directory):
    """
    Process all R and Python files under output directory, appending each file's function definitions only to subsequent files.
    """
    files = sorted(glob.glob(os.path.join(directory, '*.R')) + glob.glob(os.path.join(directory, '*.py')))
    for index, source_file in enumerate(files):
        source_functions = extract_functions_from_file(source_file)
        prepend_functions_to_subsequent_files(source_functions, files, index)
'''
# Example usage
directory = './output_directory'  # Specify your directory containing R and Python files
process_directory(directory)
'''
