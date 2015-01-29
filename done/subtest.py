import subprocess, sys
import time
child = subprocess.Popen(["ping","-c","5","www.google.com"])
child.wait()
print("parent process")

