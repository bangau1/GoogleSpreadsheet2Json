#!/usr/bin/env python

__author__ = 'agp.csui08@gmail.com (Agung Pratama)'

import gdata.spreadsheet.service
import gdata.spreadsheet
import getopt
import sys
import string
from threading import Thread
import os
import time
import json
import re
import codecs
from collections import OrderedDict

class TypeEnum:
  INT = "int"
  FLOAT = "float"
  BOOL = "bool"
  STRING = "str"
  INT_ARRAY = "int[]"
  FLOAT_ARRAY = "f[]"
  NONE = "None"

class FileHelper:
  @staticmethod
  def exists(filepath):
    return os.path.exists(filepath)
  @staticmethod
  def makedirsifnotexists(filepath):
    folderpath = os.path.dirname(filepath)
    if not FileHelper.exists(folderpath):
      os.makedirs(folderpath)

class Parse(Thread):
  def __init__(self, name, dirpath, gdServiceClient, spreadsheetKey, worksheetEntry):
    self.hasInit = False
    Thread.__init__(self)
    self.name = name
    self.dirpath = dirpath
    self.gd_client = gdServiceClient
    self.spreadsheetKey = spreadsheetKey
    self.worksheetEntry = worksheetEntry
    self.hasInit = True

  def run(self):
    self.isRunning = True
    try:
      ws_id = self.worksheetEntry.id.text.rsplit('/',1)[1]
      cellFeed = self.gd_client.GetCellsFeed(self.spreadsheetKey, ws_id, cell=None, query=None, visibility='private', projection='basic')
      
      datas = self.parseCell(cellFeed)
      content = json.dumps(datas, ensure_ascii=False, separators=(',',':'))

      filepath = self.dirpath+"/"+self.name+".json"
      FileHelper.makedirsifnotexists(filepath)
      jsonFile = codecs.open(filepath, "w", "utf-8")
      jsonFile.write(content)
      jsonFile.close()
    except Exception as e:
      print e
    self.isRunning = False

  def parseCell(self, cellFeed):
    self.lines = {}
    self.names = {}
    self.orderedOfNames = {}
    self.types = {}

    CELL_ID_REGEX = "^R(?P<row>[0-9]+)C(?P<column>[0-9]+)$"
    maxRow = -1
    maxColumn = -1

    for cellEntry in cellFeed.entry:
      cellId = cellEntry.id.text.rsplit('/', 1)[1]
      match = re.search(CELL_ID_REGEX, cellId)

      row = int(match.group("row"))-1
      column = int(match.group("column"))-1
      value = cellEntry.content.text;
      
      maxColumn = max(maxColumn, column)
      maxRow = max(maxRow, row)
      
      if row == 0:
        self.names[column] = value
        self.orderedOfNames[value]=column
      elif row == 1:
        self.types[column] = Parse.GetTypeFromString(value) 
      else:
        if not (row-2) in self.lines:
          self.lines[row-2] = {}
        self.lines[row-2][column] = value

    #build the data
    datas = []
    for row in range(2,maxRow+1):
      if not row-2 in self.lines:
        continue

      lineData = {}
      for column in range(0, maxColumn+1):
        if not column in self.names:
          continue
        fieldName = self.names[column]
        typeEnum = TypeEnum.NONE
        if column in self.types:
          typeEnum = self.types[column]
        if typeEnum == TypeEnum.NONE:
          continue
        val = Parse.GetDefaultValue(typeEnum)
        if column in self.lines[row-2]:
          val = Parse.GetValue(self.lines[row-2][column], typeEnum)

        lineData[fieldName] = val
      #end of for-column

      #sort the linedata
      lineData = OrderedDict(sorted(lineData.items(), key=lambda t:self.orderedOfNames[t[0]]))
      datas.append(lineData)
    
    #end of for-row
    return datas;

  def isFinish(self):
    return self.hasInit and not self.isRunning;

  @staticmethod
  def GetDefaultValue(typeEnum):
    if typeEnum == TypeEnum.INT:
      return 0
    elif typeEnum == TypeEnum.BOOL:
      return False
    elif typeEnum == TypeEnum.FLOAT:
      return 0
    elif typeEnum == TypeEnum.STRING:
      return None
    elif typeEnum == TypeEnum.INT_ARRAY:
      return []
    elif typeEnum == TypeEnum.FLOAT_ARRAY:
      return []
    else:
      return None

  @staticmethod
  def GetValue(value, typeEnum):
    if typeEnum == TypeEnum.INT:
      return int(value)
    elif typeEnum == TypeEnum.BOOL:
      if value.lower() == "false" or value.lower() == "0" or value == "" or value == None:
        return False
      return bool(value)
    elif typeEnum == TypeEnum.FLOAT:
      return float(value)
    elif typeEnum == TypeEnum.STRING:
      return value.decode("utf-8")
    elif typeEnum == TypeEnum.INT_ARRAY:
      return map(int, value.split(","))
    elif typeEnum == TypeEnum.FLOAT_ARRAY:
      return map(float, value.split(","))
    else:
      return None

  @staticmethod
  def GetTypeFromString(typeStr):
    t = typeStr.lower()
    if t == "int" or t == "integer":
      return TypeEnum.INT;
    elif t == "bool" or t == "boolean":
      return TypeEnum.BOOL;
    elif t == "str" or t == "string":
      return TypeEnum.STRING;
    elif t == "float" or t == "double":
      return TypeEnum.FLOAT;

    elif t == "int[]" or t == "integer[]":
      return TypeEnum.INT_ARRAY;
    elif t == "float[]" or t == "double[]":
      return TypeEnum.FLOAT_ARRAY;
    else:
      return TypeEnum.NONE

class DownloadJson:
  def __init__(self, email, password, spreadsheetKey, folder, filterWS):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService(email,password,"Json Download");
    self.spreadsheetKey = spreadsheetKey
    self.gd_client.ProgrammaticLogin()
    self.folder = folder
    self.filterWS = filterWS

  def Run(self):
    worksheetsFeed = self.gd_client.GetWorksheetsFeed(self.spreadsheetKey)
    workers = []
    for ws in worksheetsFeed.entry:
      if self.filterWS != None and (not ws.title.text in self.filterWS):
        continue
      print "process:", ws.title.text
      worker = self.ProcessWorksheetThread(ws)
      worker.start()
      workers.append(worker)
    isFinishAll = False
    while not isFinishAll:
      isFinishAll = True
      for worker in workers:
        isFinishAll = isFinishAll and worker.isFinish()


  def ProcessWorksheetThread(self, worksheetEntry):
    return Parse(worksheetEntry.content.text, self.folder, self.gd_client, self.spreadsheetKey, worksheetEntry)

def download(username, password, spreadsheetKey, foldername="temp", filterWS=[]):
  t0 = time.time()
  downloader = DownloadJson(username, password, spreadsheetKey, foldername, filterWS)
  downloader.Run()
  print "Finished in :", (time.time()-t0)

def main():
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "u:p:k:f:", ["user=", "pw=", "key=", "folder="])
  except getopt.error, msg:
    print 'python gspreadsheet2json.py --user=[username] --pw=[password] --key=[spreadsheetKey] --folder=[foldername] [filename1 [file2 [file3] ] ]'
    sys.exit(2)
  
  user = ''
  pw = ''
  key = ''
  folder = ''
  filterWS = args
  if len(filterWS) == 0:
    filterWS = None
  
  for o, a in opts:
    if o == "--user" or o == "-u":
      user = a
    elif o == "--pw" or o == "-p":
      pw = a
    elif o == "--key" or o == "-k":
      key = a
    elif o == "--folder" or o == "-f":
      folder = a
  
  if user == '' or pw == '' or key == '':
    print 'python gspreadsheet2json.py --user=[username] --pw=[password] --key=[spreadsheetKey] --folder=[foldername] [filename1 [file2 [file3] ] ]'
    sys.exit(2)
  download(username=user, password=pw, spreadsheetKey=key, foldername=folder, filterWS=filterWS)

if __name__ == '__main__':
  main()
