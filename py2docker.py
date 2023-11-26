import subprocess
import os
import glob

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e.stderr}")
        raise

def reprozip_pack_unpack(script_path):
    # ReproZip 打包
    pack_command = f"reprozip trace python {script_path}"
    run_command(pack_command)

    # ReproZip 打包文件名
    rpz_file = os.path.basename(script_path).split('.')[0] + '.rpz'

    pack_command = f"reprozip pack {rpz_file}"
    run_command(pack_command)

    # ReproZip 解包为 Docker 镜像
    unpack_command = f"reprozip docker {rpz_file}"
    run_command(unpack_command)

if __name__ == "__main__":
    output_dir = './example/output'
    for script_path in glob.glob(os.path.join(output_dir, 'cell_*.py')):
        reprozip_pack_unpack(script_path)
        print("cell_*.py complete")
