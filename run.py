import os
import subprocess
import time
import sys
import configparser
from pathlib import Path
import progressbar
# 创建 ConfigParser 对象
config = configparser.ConfigParser()

# 跨平台配置文件路径处理
current_dir = Path(__file__).resolve().parent
config_path = current_dir/"config"/"config.ini"
config.read(config_path)

# 控制最大并发进程数
MAX_PROCESSES = int(config["MAXPROCESS"]["max"])

def run_subprocess(file_path):
    # 使用Path对象确保跨平台兼容性
    script_path = current_dir/"src" / "translate_comments.py"
    
    # 统一使用Path对象作为参数
    process = subprocess.Popen(
        [sys.executable, str(script_path), str(file_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    return process

def mut_process(directory, max_processes):
    active_processes = []
    directory = Path(directory)  # 转换为Path对象

    # 使用Path.rglob递归遍历所有文件
    file_paths = [f for f in directory.rglob('*') if f.is_file()]
    num  = len(file_paths)
    bar = progressbar.ProgressBar(max_value=num)
    processed_file = 0
    for file_path in file_paths:
        while len(active_processes) >= max_processes:
            # 检查并清理完成的进程
            for p in list(active_processes):
                if p.poll() is not None:
                    stdout, stderr = p.communicate()
                    if stdout:
                        print(f"[STDOUT] {stdout.strip()}")
                    if stderr:
                        print(f"[STDERR] {stderr.strip()}")
                    active_processes.remove(p)
                    num-=1
                    processed_file+=1
                    print("{0} files remian\n".format(num))
                    bar.update(processed_file)
                    print("\n")
            
            if len(active_processes) >= max_processes:
                time.sleep(0.5) 

        # 启动新子进程
        process = run_subprocess(file_path)
        
        active_processes.append(process)
        
        print(f"processing：{file_path}")

    # 等待所有剩余子进程完成
    while active_processes:
        for p in list(active_processes):
            if p.poll() is not None:
                stdout, stderr = p.communicate()
                if stdout:
                    print(f"[STDOUT] {stdout.strip()}")
                if stderr:
                    print(f"[STDERR] {stderr.strip()}")
                active_processes.remove(p)
                num-=1
                processed_file+=1
                print("{0} files remian\n".format(num))
                bar.update(processed_file)
                print("\n")
        time.sleep(0.5)
    bar.finish()

if __name__ == '__main__':
    print("###########################################################################\n")
    print("Developed by jianfeeeee. Welcome to use! (Distributed under the MIT License)\n")
    print("###########################################################################\n")
    if len(sys.argv) >1:
        project_dir = sys.argv[1]

    else:
        project_dir = input("Enter target directory (all subdirectories will be translated):")
    mut_process(project_dir, MAX_PROCESSES)
    print("all target processed")
