
import glob
import os
files=[]
# os.chdir(r'/Users/kgt/Desktop/url_capture/')
txtPath="./texts/"
for file in os.listdir(txtPath):
    # print(file)
    if file.endswith(".txt"):
        files.append(os.path.join(txtPath, file))
print(files)

def writeToFile(thisset):
    outputFile = "input-keywords.txt"
    with open(outputFile, 'a+') as f:
        for line in thisset:
            if len(line.strip()) != 0 :
                f.write(line.strip())
                f.write('\n')

for file in files:
    inputTextFile = open(file, 'r')
    Lines = inputTextFile.readlines()
    writeToFile(Lines)
    inputTextFile.close