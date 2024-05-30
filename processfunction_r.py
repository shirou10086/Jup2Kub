import glob
import re
import os

def extract_functions_from_file(file_path):
    """
    Extract R function definitions from a file.
    """
    function_pattern = re.compile(r"(\b\w+\s*<- function\(.*?\)\s*\{.*?\n\})", re.DOTALL)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        functions = function_pattern.findall(content)
    return {f.split('<-')[0].strip(): f for f in functions}  # 返回函数名称与定义的映射

def prepend_functions_to_subsequent_files(source_functions, all_files, original_file_index):
    """
    Prepend function definitions to subsequent R files in the list, ensuring no duplicates.
    """
    for file_path in all_files[original_file_index+1:]:  # 只考虑源文件之后的文件
        with open(file_path, 'r+', encoding='utf-8') as file:
            content = file.read()
            prepend_content = ''
            for func_name, func_def in source_functions.items():
                if func_name not in content:  # 检查函数是否已存在
                    prepend_content += func_def + '\n\n'  # 准备前置内容
            if prepend_content:
                file.seek(0)  # 移动到文件开始位置
                file.write(prepend_content + content)  # 写入新的函数定义和原有内容
                print(f"Prepended new functions to {file_path} from {all_files[original_file_index]}.")

def process_directory(directory):
    """
    Process all R files in a directory, appending each file's function definitions only to subsequent files.
    """
    r_files = sorted(glob.glob(os.path.join(directory, '*.R')))  # 确保文件按顺序处理
    for index, source_file in enumerate(r_files):
        source_functions = extract_functions_from_file(source_file)
        prepend_functions_to_subsequent_files(source_functions, r_files, index)
'''
# Example usage
directory = './output_directory'  # Specify your directory containing R files
process_directory(directory)
'''
