import json

def nextPowerOf2(n): 
  
    p = 1
    if (n and not(n & (n - 1))): 
        return n 
  
    while (p < n) : 
        p <<= 1
          
    return p; 


def readJSON(text):
    objs = []
    decoder = json.JSONDecoder()
    s_len = len(text)
    end = 0

    while end != s_len:
        try:
            obj, end = decoder.raw_decode(text, idx=end)
            objs.append(obj)
        except ValueError:
            end += 1

    return objs

def readConfig(path: str): 
    file = open(path, 'r')
    file = file.read()

    return readJSON(file)