"""
read out the values from CIRASAME

2024.01.26 R.Okazaki
"""

import os
import sys
import time
import yaml
import argparse
import subprocess as sub
import numpy as np
import PySimpleGUI as sg

#SCAN_DAC_VALUE = [150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200]
SETTING_FILE_PATH = 'yaml_files/settings.yml'


#args -> --name (default is "data_default"), --settings
#getting arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n','--name', default='data_default')
#parser.add_argument('-s','--settings', default='yaml_files/settings.yml')
args = parser.parse_args()

#if args.settings == None:
#    print('error: No argument for --settings')
#    sys.exit()

#generating data directry
if not os.path.exists('data'):
    os.makedirs('data')
    if not os.path.exists('data/'+args.name):
        os.makedirs('data/'+args.name)
        if not os.path.exists('data/'+args.name+'/binary'):
            os.makedirs('data/'+args.name+'/binary')
        if not os.path.exists('data/'+args.name+'/decimal'):
            os.makedirs('data/'+args.name+'/decimal')

#loading settings (save your default settings at "yaml_files/settings.yaml")
with open(SETTING_FILE_PATH, encoding='utf-8') as f:
    settings = yaml.safe_load(f)

CITIROC_PATH = settings['CITIROC_path']
HUL_PATH     = settings['HUL_path']
YAML_PATH    = settings['YAML_path']
CIRASAME_IP  = settings['CIRASAME_ip']
DAC_SCAN     = settings['DAC_scan']


scan_dac_value = []

for i in range(int(DAC_SCAN['steps'])):
    scan_dac_value.append(int(DAC_SCAN['start'])+i*int(DAC_SCAN['gap']))

#setting progress bar
sg.theme('Dark Red')
PROGRESS_MAX = len(scan_dac_value)
current_progress = 0
layout = [[sg.Text('taking data...')],
          [sg.ProgressBar(PROGRESS_MAX, orientation='h', size=(20,20), key='-PROG-')],
          [sg.Cancel()]]
window = sg.Window('scaler reader', layout)

t_start = time.time()


#main part of reading scaler
for dac in scan_dac_value:
    
    with open('yaml_files/RegisterValue.yml', 'r') as f:
        yml_RegVal = yaml.safe_load(f)
    print('start : DAC2 = {}'.format(str(dac)))
    yml_RegVal['CITIROC1']['DAC2 code'] = dac
    yml_RegVal['CITIROC2']['DAC2 code'] = dac
    yml_RegVal['CITIROC3']['DAC2 code'] = dac
    yml_RegVal['CITIROC4']['DAC2 code'] = dac
    with open('yaml_files/RegisterValue.yml', 'w') as f:
        yaml.dump(yml_RegVal, f)
    
    event, values = window.read(timeout=10)
    if event == 'Cancel' or event == sg.WIN_CLOSED:
        break
    window['-PROG-'].update(current_progress)
    current_progress = current_progress+1

    sub.run([CITIROC_PATH+'/femcitiroc_control', '-ip='+CIRASAME_IP, '-yaml='+YAML_PATH+'/RegisterValue.yml', '-sc', '-read', '-q'])
    sub.run([HUL_PATH+'/write_register', CIRASAME_IP, '0x80000000', '0x1', '1'])
    time.sleep(1)
    sub.run([HUL_PATH+'/read_scr', CIRASAME_IP, args.name+'/binary/dataBin{}.dat'.format(str(dac))])
    print(yml_RegVal['CITIROC1']['DAC2 code'])
    
t_end = time.time()

# rewriting binary data to decimal data
for i in scan_dac_value:
    i = int(i)
    output_str = sub.run(['od', '-Ad', '-td', '-v', args.name+'/binary/dataBin{}.dat'.format(str(i))], capture_output=True, text=True).stdout
    #print(output_str)
    with open(args.name+'/decimal/dataDec{}.txt'.format(str(i)), 'w') as f:
        f.write(output_str)

print(scan_dac_value)

t_elapsed = int(t_end-t_start)
hour = t_elapsed//3600
minute = (t_elapsed%3600)//60
second = (t_elapsed%3600%60)
print("elapsed time")
print(str(hour).zfill(2) + ":" + str(minute).zfill(2) + ":" + str(second).zfill(2))
