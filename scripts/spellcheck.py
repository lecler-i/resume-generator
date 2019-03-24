import re
import sys
import tempfile
import subprocess
import os

tmp_file = tempfile.NamedTemporaryFile(mode="a+")

regex_str = r": \"([^\"]*?)\""

if len(sys.argv) < 2:
    print("usage : {} filename".format(sys.argv[0]))
    sys.exit(1)

input_file = open(sys.argv[1], "r")
content = input_file.read()

for m in re.finditer(regex_str, content):
    tmp_file.write(m.group(1));
    tmp_file.write('\n');
    print(m.group(1))

tmp_file.flush()

print("Tmp file : {}".format(tmp_file.name))
input("Press Enter to edit file...")

subprocess.call([os.environ["EDITOR"], tmp_file.name] + sys.argv[2:])
output_file_name = input("Write to file [{}]: ".format(input_file.name)) or input_file.name

tmp_file.seek(0)
with open(output_file_name, "w+") as f:
    f.write(re.sub(regex_str, lambda x: ": \"{}\"".format(tmp_file.readline().strip()), content))

