import subprocess
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str)
parser.add_argument('--name', type=str)
args = parser.parse_args()
if args.path == None:
    print("Call with --name <path/to/message/to/send>")
else:
    text_path = args.path
print(text_path)
if args.name == None:
    print("Call with --name <EXACT NAME>  --> capitalization matters")
else:
    buddy = args.name


f = open(text_path, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip('\n')
    subprocess.Popen(['osascript', 'send_msg.script', line, buddy])
    time.sleep(.1)
