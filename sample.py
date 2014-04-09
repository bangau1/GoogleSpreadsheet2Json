#!/usr/bin/env python
import gspreadsheet2json
import getpass
import os
import shutil

if __name__ == "__main__":
	
	#prompt the gmail
	user = raw_input("Your gmail:")

	#get password without reveal it on terminal
	pw = getpass.getpass(user+"'s password:\n")

	spreadsheetKey = raw_input("Your spreadsheet key:")

	#outputfolder"
	outFolder = "temp" 

	#remove old temp file if exists
	if os.path.exists(outFolder):
		shutil.rmtree(outFolder)

	#the worksheet names you want to download.
	#by default if you set it as None or empty list, then it will download all worksheets available on the spreadsheet
	filteredWS = []

	gspreadsheet2json.download(username=user, password=pw, spreadsheetKey=spreadsheetKey, foldername=outFolder, filterWS=filteredWS)