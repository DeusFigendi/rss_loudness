#!/usr/bin/env python3

import feedparser
import urllib.request
import subprocess
import os
import sys
import json

# This progam analyses the mp3 files of an rss feed (vulgo: podcast) and saves them into a file
#
# usage:
# python3 rss_loudness.py feed_url [float_delimiter [output_format [first_episode_number]]]
#
# feed_url (obligatory):           The url of the feed to analyse
# float_delimiter (optional):      In the output file float numbers could be represented with . or with , (default) as decimal delimiter or any other character string (like \t e.g.)
# output_format (optional):        Defaults to csv. Alternative is json
# first_episode_number (optional): To set which episode number the first episode has (usually 0 or 1)


feed_url = "https://letscast.fm/podcasts/darwin-pod-dd57bfef/feed"
float_delimiter = ','
output_format = "csv"
first_episode_number = 0
	
if len(sys.argv) >= 5:
	feed_url = sys.argv[1]
	float_delimiter = sys.argv[2]
	output_format = sys.argv[3]
	first_episode_number = int(sys.argv[4])
elif len(sys.argv) == 4:	
	feed_url = sys.argv[1]
	float_delimiter = sys.argv[2]
	output_format = sys.argv[3]
elif len(sys.argv) == 3:	
	feed_url = sys.argv[1]
	float_delimiter = sys.argv[2]
elif len(sys.argv) == 2:	
	feed_url = sys.argv[1]
else:
	print('it should not happen that no parameter is given')
	os.terminate('no feed given')


def get_mp3_file(linklist):
	# returns the url of the link where the "rel" is "enclosure"
	for i in linklist:
		if i['rel'] == 'enclosure':
			return(i['href'])
	return(False)

def get_loudnesses_from_file(f):
	# this function is "inspired" by loudness-cli by Dan Rossi which is based on loudness by Neg23 (see licence at the end of the document)
	# https://github.com/danrossi/loudness-cli
	# https://github.com/kylophone/neg23
	# This function returns a dict of loudness values of a given filename
	ffargs = ["ffmpeg",
			'-nostats',
			'-i',
			f,
			'-filter_complex',
			'[a:0]ebur128',
			'-f',
			'null'
			,'-']
	proc = subprocess.Popen(ffargs, stderr=subprocess.PIPE)
	stats = str(proc.communicate()[1])
	summaryList = stats[stats.rfind('Summary:'):].split()
	
	ILufs = float(summaryList[summaryList.index('I:') + 1])
	IThresh = float(summaryList[summaryList.index('I:') + 4])
	LRA = float(summaryList[summaryList.index('LRA:') + 1])
	LRAThresh = float(summaryList[summaryList.index('LRA:') + 4])
	LRALow = float(summaryList[summaryList.index('low:') + 1])
	LRAHigh = float(summaryList[summaryList.index('high:') + 1])
	statsDict = {'I': ILufs, 'I Threshold': IThresh, 'LRA': LRA,
                 'LRA Threshold': LRAThresh, 'LRA Low': LRALow,
                 'LRA High': LRAHigh}    
	return(statsDict)

def eurofloat(f):
	# returns float with coma instead of point as decimal delimiter 
	return_string = str(f).replace('.',',')
	return(return_string)

NewsFeed = feedparser.parse(feed_url)

csv_content = '"index";"Title";"I";"I Threshold";"LRA";"LRA T";"LRA L";"LRA H"'+"\n"
json_content = []

for j in range(0,len(NewsFeed.entries)):
	i = len(NewsFeed.entries)-j-1
	this_title = NewsFeed.entries[i]['title'].replace('"',"'")
	this_mp3_url = get_mp3_file(NewsFeed.entries[i]['links'])
	print(this_title+ ' - '+this_mp3_url)
	urllib.request.urlretrieve(this_mp3_url, str(j+first_episode_number)+".mp3")
	this_loudness = get_loudnesses_from_file(str(j+first_episode_number)+".mp3")
	os.remove(str(j+first_episode_number)+".mp3")
	csv_content += str(j+first_episode_number)+';"'+this_title+'";'+eurofloat(this_loudness['I'])+';'+eurofloat(this_loudness['I Threshold'])+';'+eurofloat(this_loudness['LRA'])+';'+eurofloat(this_loudness['LRA Threshold'])+';'+eurofloat(this_loudness['LRA Low'])+';'+eurofloat(this_loudness['LRA High'])+"\n"
	json_content.append({**this_loudness, **{'index':j+first_episode_number,"title":this_title}})
	if output_format == "csv":
		with open("loudness.csv", "w") as csv_file:
			csv_file.write(csv_content)
	elif output_format == "json":
		with open('loudness.json', 'w') as json_file:
			json.dump(json_content, json_file)
	else:
		print('unknown output format: '+output_format)
		os.terminate('unknown output format: '+output_format)

print('Done')



# The MIT License (MIT)
#
# Copyright (c) 2024 Deus Figendi based on Dan Rossi https://github.com/danrossi/loudness-cli based on Neg23 https://github.com/kylophone/neg23
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

