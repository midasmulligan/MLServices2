import os
from fabric.api import local


path = os.getcwd()
for root, dirs, files in os.walk(path):
    for name in files:
        if name.endswith(("~", ".pyc", ".pkl", ".bak", ".dir", ".out", ".dat", ".zip" )):
            fullWithFullPath = root +"/" + name
            local("rm -rf "+ fullWithFullPath)
