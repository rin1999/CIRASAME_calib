import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import re
import glob
import numpy as np
from scipy.optimize import curve_fit

parser = argparse.ArgumentParser()
parser.add_argument('-ch','--channel', default='0')
args = parser.parse_args()

READ_CH = int(args.channel)
read_row = int(READ_CH/4)
read_col = READ_CH%4

DIR_PATH = '20240206_1/decimal'
file_list = glob.glob(os.path.join(DIR_PATH, "*.txt"))

hits = []       # Number of counts
hits_log = []   # Number of counts in log10
dac_val = []    # Value of dac input

#print(READ_CH)

for file_path in file_list:
    file_name = os.path.basename(file_path)
    print('now reading '+file_name)
    v_dac = int(re.sub(r"\D", "", file_name))
    df = pd.read_table(file_path, delim_whitespace=True, header=None)
    clock = df.iat[0,1]
    if clock == 0:
        continue
    #hits.append(df.iat[read_row+2, read_col+1]/clock*125000000)
    if df.iat[read_row+2, read_col+1] == 0:
        hits_log.append(np.log10(1/clock*125000000))
        hits.append(1/clock*125000000)
    else:
        hits_log.append(np.log10(df.iat[read_row+2, read_col+1]/clock*125000000))
        hits.append(df.iat[read_row+2, read_col+1]/clock*125000000)
    dac_val.append(v_dac)

# sorting the lists
dac_val, hits_log, hits = zip(*sorted(zip(dac_val, hits_log, hits)))
dac_val = list(dac_val)
hits_log = list(hits_log)
hits = list(hits)

"""
def sigmoid_func(x, x0, a, b, c): #for fitting
    #if x<0:
        return a/(1+np.exp(-b*(x-x0))) + c
    #else:
    #    return np.exp(a*(x-x0))/(np.exp(a*(x-x0))+1)
"""

# calc gradient
hits_grad = []

for i in range(len(dac_val)):
    if i == 0:
        grad = (hits_log[i+1]-hits_log[i])/(dac_val[i+1]-dac_val[i])
        hits_grad.append(grad)
    elif i == len(dac_val)-1:
        grad = (hits_log[i]-hits_log[i-1])/(dac_val[i]-dac_val[i-1])
        hits_grad.append(grad)
    else:
        #grad = (hits[i+1]-hits[i-1])/(dac_val[i+1]-dac_val[i-1])
        grad = (hits_log[i+1]-hits_log[i-1])/(dac_val[i+1]-dac_val[i-1])
        hits_grad.append(grad)

def fit_func(x, offset, a1, a2, a3, a4, b1, b2, b3, b4, c1, c2, c3, c4):

    return offset + a1*np.exp(-(x-b1)/(2*c1)) + a2*np.exp(-(x-b2)/(2*c2)) + a3*np.exp(-(x-b3)/(2*c3)) + a4*np.exp(-(x-b4)/(2*c4))

# calc grad average
hits_grad_ave = []

# average of 3 values

for i in range(len(hits_grad)):
    if i == 0:
        hits_grad_ave.append((hits_grad[i]+hits_grad[i+1])/2)
    elif i == len(hits_grad)-1:
        hits_grad_ave.append((hits_grad[i-1]+hits_grad[i])/2)
    else:
        hits_grad_ave.append((hits_grad[i-1]+hits_grad[i]+hits_grad[i+1])/3)

'''
for i in range(len(hits_grad)):
    if i == 0:
        hits_grad_ave.append((hits_grad[i]+hits_grad[i+1])/2)
    elif i == len(hits_grad)-1:
        hits_grad_ave.append((hits_grad[i-1]+hits_grad[i])/2)
    else:
        hits_grad_ave.append((hits_grad[i-1]+hits_grad[i]+hits_grad[i+1])/3)
'''

plt.scatter(dac_val, hits_grad_ave)
#plt.plot(x_plot, fitted_function, 'r-')
#plt.yscale('log')
plt.xlabel('threshold (DAC value)')
plt.ylabel('gradient of hits')
plt.grid(True)
plt.show()
