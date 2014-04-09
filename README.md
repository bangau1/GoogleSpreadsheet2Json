GoogleSpreadsheet2Json
====
**Only for python 2.6.x or 2.7.x**

This script will allow you to download Spreadsheet's worksheets as json format.


## Installation

1. Download & Install gdata-python-client Library

	Go to the [link](https://code.google.com/p/gdata-python-client/downloads/list) and download the latest library(eq: gdata-2.0.18.zip). Extract the zip file and follow the setup instruction from there.
	
	
2. Download & Install GoogleSpreadsheet2Json 
	
	a. Download GoogleSpreadsheet2Json's zip file and uncompress it. 
	
	b. If your python version is not 2.7.x (which is 2.6.x), then please install `ordereddict` module :

		`pip install ordereddict`
	
	c. Run `python setup.py install` to install the library.

## Sample Usage
### Setup Example Spreadsheet

1. Create new spreadsheet on your Google Drive. 

2. Writedown the spreadsheetkey. You can get the key from the URL on the browser. If the url is like this: `https://docs.google.com/spreadsheet/ccc?key=0AtNKAJYAGxJ1dFhuVnBlZzQ0V1Rhck13Qk5lR2lMeGc#gid=0` then the key will be `0AtNKAJYAGxJ1dFhuVnBlZzQ0V1Rhck13Qk5lR2lMeGc`.

3. Rename the sheet as you like, rename the worksheet's name, and put into it the data with the format like the public spreadsheet I've created [here](https://docs.google.com/spreadsheet/ccc?key=0AtNKAJYAGxJ1dFhuVnBlZzQ0V1Rhck13Qk5lR2lMeGc#gid=0).

![Screenshot](https://dl.dropboxusercontent.com/u/14494023/screenshot-spreadsheet.png)

### Sample Code

You can find the sample code on **sample.py** from the source code of this git.

```
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
```

Now run the **sample.py** on terminal ``python sample.py``, and it wil prompt the gmail, password of your gmail, and the spreadsheet key. 

You can pass `0AtNKAJYAGxJ1dFhuVnBlZzQ0V1Rhck13Qk5lR2lMeGc` as the spreadsheet key, as I have made my spreadsheet as public, so anyone can view/download it. But, before that, you have to open the spreadsheet's link first [here](https://docs.google.com/spreadsheet/ccc?key=0AtNKAJYAGxJ1dFhuVnBlZzQ0V1Rhck13Qk5lR2lMeGc#gid=0). 

 If the authentication process is successful, it will download all the .json files inside the output folder you pass on the script. If you use my spreadsheet, then it will download 2 json file: **example_ws.json** and **other_ws.json**


## Rule and Limitation

There are some rule and limitation for this current version of gspreadsheet2json:

1. On the google worksheet, all columns's content of the **first row** will be the name of json property. For example of my spreadsheet, it will be: `id`, `name`, `others`, etc.
2. The second row will be for json datatypes. Current supported datatypes are: 

	| Second Row's content 		| Mapped into data type| Output Example (assuming the property name is `data`)	| 
| :--: 					| :--: 					| :--:|
| `int`, `integer`   	|`int`    				| "data":123|
| `double`, `float`    	|`float`    			| "data":3.14123|
| `bool`, `boolean`    	|`bool`   				| "data":True, "data":False|
| `str`, `string`		|`string` 				| "data":"You can put utf-8 character too like 何これ？"|
| `int[]`, `integer[]` 	|`int[]`    			| "data":[12, 34, 0, 123, 9]|
| `double[]`, `float[]`	|`float[]`    			| "data":[1.09, 1.00, 12.31]|

	If the datatype column's content is not listed in the *Second Row's content*, it will be skipped. For example: `comment` on the F3 (like my spreadsheet example), then that column will be skipped.
	
3. The downloaded json will be top-level json array ~~not top-level json object~~

	Example : `[{"id":1, "data":"this is B3"}, {"id":2, "data":"this is B4"}]`.
	
	


