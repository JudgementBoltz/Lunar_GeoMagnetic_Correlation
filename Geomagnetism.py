import os
import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def pathgenerator():
    dir_tree = os.walk("C:\magweb.cr.usgs.gov\data\magnetometer")
    dir_paths = [x for x in dir_tree]
    dir_tree = dir_paths[0][1]
    directories = []
    for i in dir_tree:
        directories.append("\\".join([dir_paths[0][0], i], "OneMinute"))
    return directories

def GetLunarData():       
    #grabs the html code of the page containing our lunar cycle data
    html = requests.get("http://aa.usno.navy.mil/cgi-bin/aa_phases.pl?year=2013&month=6&day=1&nump=99&format=t").text
    html2 = requests.get("http://aa.usno.navy.mil/cgi-bin/aa_phases.pl?year=2015&month=6&day=1&nump=99&format=t").text
    #creates a beautiful soup object
    soup = BeautifulSoup(html, 'html5lib')
    soup2 = BeautifulSoup(html2, 'html5lib')
    #gets all table cell data, all odd cells will be moon phase all even cells date/time
    LunarData = soup.find_all('td')
    LunarData2 = soup2.find_all('td')
    #strips <td> and </td> from each cell returns data as a list of strings
    data = [str(td)[4:-5] for td in LunarData]

    #Last quarter
    last_quarter = []
    L1 = data[0]
    #New moon
    new_moon = []
    L2 = data[2]
    #First quarter
    first_quarter = []
    L3 = data[4]
    #Full moon
    full_moon = []
    L4 = data[6]

    #These loops separate the dates into 4 lists based on the phase of the moon at that date
    #this is necessary because we will want to examine each unique moon phase
    for i in range(1,199,2):
        if data[i-1] == L1:
            last_quarter.append(data[i])
        if data[i-1] == L2:
            new_moon.append(data[i])
        if data[i-1] == L3:
            first_quarter.append(data[i])
        if data[i-1] == L4:
            full_moon.append(data[i])
    
    data = [str(td)[4:-5] for td in LunarData2]        
    for i in range(1,199,2):
        if data[i-1] == L1:
            last_quarter.append(data[i])
        if data[i-1] == L2:
            new_moon.append(data[i])
        if data[i-1] == L3:
            first_quarter.append(data[i])
        if data[i-1] == L4:
            full_moon.append(data[i])
    #returns a list of the moon phase data lists
    return [first_quarter,full_moon,last_quarter,new_moon]

def GetMagData(station, time_frame, LunarPhase, count):
    time_frame = time_frame/2
    data = LunarData[LunarPhase][count]    
    date = data.split()    
    files = []
    x = datetime.datetime.strptime(date[0] + date[1] + date[2], "%Y%b%d")
    x = x - datetime.timedelta(time_frame)   

    for i in range(time_frame*2):
        x = x + datetime.timedelta(1)   
        y = datetime.datetime.strftime(x, "%Y%m%d")
        files.append(y+"vmin.min")
    return files

#set analysis parameters
station = "HON"
#even number of days to pull data for, centered around the date and time of the moonphase event
time_frame = 6
#Sets the number of lunar cycles to analyze
run = 1

#set names for column headers
names = ['DATE','TIME','DOY','H','D','Z','F']
#set working directory
os.chdir("Z:\Geomagnetism")
#color codes for plot
colors = ['red','green','blue','black']

#retrieves moonphase data from the USN moonphase database and stores in a list
#list of the form [first_quarter,full_moon,last_quarter,new_moon]
global LunarData
LunarData = GetLunarData()

#sets the global variable in the GeomagFunctions module
#GM.LunarData = LunarData

#Starts the main loop to analyze geomagnetic data
directory = "C:\magweb.cr.usgs.gov\data\magnetometer" + "\\" + station + "\\" + "OneMinute"
count = 0
files = [[],[],[],[]]
while count < run:
    #iterates through lunar phases
    for i in range(4):
        stuff = GetMagData(station, time_frame, i, count)
        files[i] = files[i] + stuff
    count += 1

phase_list = ['first_quarter','full_moon','last_quarter','new_moon']
##main loop
#iterates through each moon phase
for i in range(4):
    data_frames = pd.DataFrame()
    #iterates through selected lunar cycles
    for j in files[i]:
        #read data into data frame from file, separate by whitespace
        df = pd.read_table(directory + "\\" + "hon" + j, sep=r'\s*',skiprows=25, names=names, engine='python')
        data_frames = pd.concat([data_frames,df])
    graph = data_frames.plot(x='TIME', y='F')
    graph.axes.get_xaxis().set_visible(False)
    plt.savefig('Z:\Geomagnetism\Results\\' + phase_list[i] + '.pdf')
