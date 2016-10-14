#-*- coding: utf8 -*-
import xlrd
import re

fname = "tt.xls"
bk = xlrd.open_workbook(fname)
#shxrange = range(bk.nsheets)
try:
    sh = bk.sheet_by_name("Sheet1")
except:
    print ("no sheet in %s named Sheet1" % fname)
#获取行数
nrows = sh.nrows
#获取列数
ncols = sh.ncols
print ("nrows %d, ncols %d" % (nrows,ncols))
#获取第一行第一列数据 
#cell_value = sh.cell_value(1,1)
#print cell_value
file_object = open('thefile.txt', 'a')

#获取各行数据写到文本文件中
for i in range(0,nrows):
    row_data = sh.row_values(i)
    for k in range(0,len(row_data)):
        str1 = ('%s' % (row_data[k]))
        result = re.findall(r'1\d{10}',str1,re.M)
        if result :
            for j in range(0,len(result)):
            	print(result[j-1])
            	file_object.write(('%s\n' % (result[j-1])))
file_object.close( )
