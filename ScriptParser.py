import pandas as pd
import re

class Parser:
    def __init__(self, path):
        self.path = path

    def Parse(self):
        with open(self.path) as file:
            lines = file.readlines()

        out_file = "tmp.py"
        file = open(out_file, "w")
        file.write("import psutil\n")
        file.write("import time\n")
        file.write("p = psutil.Process()\n")
        file.write("log_time = open(\"log_time.csv\", \"w\")\n")
        file.write("log_cpu = open(\"log_cpu.csv\", \"w\")\n")
        file.write("log_ram = open(\"log_ram.csv\", \"w\")\n")
        file.write("time_dict = {}\n")
        file.write("cpu_dict = {}\n")
        file.write("ram_dict = {}\n")

        skip_list = ["#", "elif", "else", "except", "finally", "class", "break", "continue", "pass", "return"]
        nesting_list = ["for", "while", "if", "def", "with", "try"]

        skip_comment_block = False
        nested_counter = 0

        for idx in range (0, len(lines)):
            line = lines[idx]
            stripped_line = line.rstrip()   # remove \n from end of line
            if len(stripped_line) == 0:     # skip blank lines
                file.write(line)
                continue

            # Split line into words based on ' ' delimiter
            split_words = stripped_line.split(' ')

            # Special logic to handle ending of """ commend block
            if skip_comment_block == True:
                if '"""' in split_words[0]:
                    skip_comment_block = False

                continue

            # Special logic to handle begin of """ comment block
            if '"""' in split_words[0] and len(split_words) == 1:
                skip_comment_block = True
                continue

            # Handle reserved system words to skip from skip_list
            skip_this_line = False
            for skip_item in skip_list:
                if skip_item in split_words[0]:
                    file.write(line)
                    skip_this_line = True
                    break

            if skip_this_line == True:
                continue

            # Count number of whitespaces before (for tabbed lines)
            whitespaces = re.split(" |\t", stripped_line).count('')
            if whitespaces == 0:
                nested_counter = 0  # Reset counter

            if nested_counter > 0:
                nested_loop = False
                for nesting_item in nesting_list:
                    if nesting_item in split_words[0]:
                        nested_counter = nested_counter + 1
                        nested_loop = True
                        file.write(line)
                        break

                if nested_loop == True:
                    continue

                tabs = ""
                for i in range (0, nested_counter):
                    tabs = tabs + "    "
                file.write(tabs + "start_time = time.perf_counter()\n")
                file.write(tabs + "start_cpu = p.cpu_percent()\n")
                file.write(tabs + "start_ram = psutil.virtual_memory().percent\n")
                file.write(line)
                file.write(tabs + "end_time = time.perf_counter()\n")
                file.write(tabs + "end_cpu = p.cpu_percent()\n")
                file.write(tabs + "end_ram = psutil.virtual_memory().percent\n")

                stripped_key = stripped_line.strip(' ')
                stripped_key = str(idx + 1) + ", " + stripped_key.strip('\t')
                file.write(tabs + 'time_dict["' + stripped_key + '"] = end_time - start_time if time_dict.get("' + stripped_key + '") == None else time_dict["' + stripped_key + '"] + end_time - start_time\n')
                file.write(tabs + 'cpu_dict["' + stripped_key + '"] = end_cpu - start_cpu if cpu_dict.get("' + stripped_key + '") == None else cpu_dict["' + stripped_key + '"] + end_cpu - start_cpu\n')
                file.write(tabs + 'ram_dict["' + stripped_key + '"] = (end_ram - start_ram) * psutil.virtual_memory().total / 100000000 if ram_dict.get("' + stripped_key + '") == None else ram_dict["' + stripped_key + '"] + (end_ram - start_ram) * psutil.virtual_memory().total / 100000000\n')

            # Handle first time
            for nesting_item in nesting_list:
                if nesting_item in split_words[0]:
                    nested_counter = nested_counter + 1
                    file.write(line)
                    break
            
            if nested_counter > 0:
                continue

            file.write("start_time = time.perf_counter()\n")
            file.write("start_cpu = p.cpu_percent()\n")
            file.write("start_ram = psutil.virtual_memory().percent\n")

            file.write(line)

            file.write("end_time = time.perf_counter()\n")
            file.write("end_cpu = p.cpu_percent()\n")
            file.write("end_ram = psutil.virtual_memory().percent\n")

            curated_line = stripped_line.replace(r"'", r"\'")
            log_time = str(idx + 1) + "; ' + str(end_time - start_time) + '; " + curated_line
            log_cpu = str(idx + 1) + "; ' + str(end_cpu - start_cpu) + '; " + curated_line
            log_ram = str(idx + 1) + "; ' + str((end_ram - start_ram) * psutil.virtual_memory().total / 100000000) + '; " + curated_line
            file.write("log_time.write('" + log_time + "\\n')\n")
            file.write("log_cpu.write('" + log_cpu + "\\n')\n")
            file.write("log_ram.write('" + log_ram + "\\n')\n")

        file.write("for entry in time_dict:\n")
        file.write("    key_pair = entry.split(',')\n")
        file.write("    log_time.write(key_pair[0] + '; ' + str(time_dict[entry]) + ';' + key_pair[1] + '\\n')\n")

        file.write("for entry in cpu_dict:\n")
        file.write("    key_pair = entry.split(',')\n")
        file.write("    log_cpu.write(key_pair[0] + '; ' + str(cpu_dict[entry]) + ';' + key_pair[1] + '\\n')\n")

        file.write("for entry in ram_dict:\n")
        file.write("    key_pair = entry.split(',')\n")
        file.write("    log_ram.write(key_pair[0] + '; ' + str(ram_dict[entry]) + ';' + key_pair[1] + '\\n')\n")

        file.write("log_time.close()\n")
        file.write("log_cpu.close()\n")
        file.write("log_ram.close()\n")

        file.close()
        return out_file

class LogParser:
    def __init__(self):
        self.time_path = "log_time.csv"
        self.cpu_path = "log_cpu.csv"
        self.ram_path = "log_ram.csv"

    def ParseTimeLog(self):
        df = pd.read_csv(self.time_path, names=['Line','Time','Code'], delimiter=';')
        return df.sort_values('Line')

    def ParseCPULog(self):
        df = pd.read_csv(self.cpu_path, names=['Line','CPU','Code'], delimiter=';')
        return df.sort_values('Line')

    def ParseRAMLog(self):
        df = pd.read_csv(self.ram_path, names=['Line','RAM','Code'], delimiter=';')
        return df.sort_values('Line')
