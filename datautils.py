# Python utility functions for reading in data, etc.

import sys, os, copy, subprocess
import numpy as np

error1 = "Input to ListDataFrame should be a list of lists or list of numpy arrays"
error2 = "Input column is not the same length as existing columns in ListDataFrame"


# Fast line-counting approach to deal with really large files
# (e.g., with 350,000-line file, this takes 0.4s, vs 1.4s for the more Pythonic
# return len([ line for line in open(fname)])
def CountLinesInFile( fname ):
	p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	result, err = p.communicate()
	if p.returncode != 0:
		raise IOError(err)
	return int(result.strip().split()[0])

# Slower method which counts "data" lines only:
def CountDataLinesInFile( fname, skip="#" ):
	return len([ line for line in open(fname) if len(line.strip()) > 0 and line[0] not in skip ])



class ListDataFrame(object):
	"""A class designed to hold a 2D list array (a list of lists, each of the
	latter being "columns" and presumably having the same length), corresponding
	to some table of data.  Individual columns should have a single data type,
	but different columns can have different data types (e.g., one column can
	be strings, another integers, and a third floating point numbers).
	Columns can also be NumPy arrays.
	
	Optionally, a list of column names for the array can be supplied, or
	added later; extra column-name lists can also be added after creation.
	When indexed with one of the column names (e.g., obj["radius"]), it acts
	like a dictionary and returns the corresponding column.  When indexed
	with an integer or a slice, it acts like the underlying list of lists.
	
	If the column names are strings, then they also become attributes
	of the object instance and can be accessed as, e.g., obj.radius -- as
	long as the names are valid Python identifiers (must contain only
	alphanumerica or _ and must start with letter or _).
	
	Example: if the first column corresponds to column name "radius", then
	it can be accessed as: obj[0], obj["radius"], or obj.radius (and also
	as obj.data[0]).
	
	The original list-of-lists is always accessible via obj.data
	
	If you have data that are all floating-point, it's probably better to
	turn it into a big NumPy array and use the ArrayDataFrame class instead.
	"""

	def __init__(self, dataList, columnNames=None):
		if type(dataList) != list:
			raise TypeError(error1)
		if type(dataList[0]) not in [list, np.ndarray]:
			raise TypeError(error1)
		self.data = dataList
		self.colNames = columnNames
		self.dict = {}
		
		self.nCols = len(dataList)
		if self.colNames is not None:
			self.SetColumns(columnNames)
	
	def __getitem__(self, key):
		"""Defines behavior of indexing: indexing with strings causes
		internal column-name dictionary to be accessed (returns corresponding
		column of data array); indexing with anything else (e.g., integers or
		slices) is passed on to the data array.
		"""
		ktype = type(key)
		if ktype is str:
			return self.dict[key]
		else:
			return self.data[key]
	
	def __str__(self):
		outString = str(self.data)
		if self.colNames is not None:
			outString = str(self.colNames) + "\n" + outString
		return outString
	
	def SetColumns(self, columnNames):
		"""Define the column names (dictionary keys pointing to columns
		within the data frame).
		columnNames should be a list of objects (usually strings).
		If called more than once, erases previous column-name definitions.
		"""
		
		if self.dict != {}:
			# remove old column definitions
			for oldName in self.dict:
				# remove old column-name attributes
				oldName_attr = oldName.split()[0].strip()
				if oldName_attr in self.__dict__:
					junk = self.__dict__.pop(oldName_attr)
			self.dict = {}
		for i in range(self.nCols):
			try:
				colName = columnNames[i]
				self.dict[colName] = self.data[i]
				# define a new attribute, if possible (for access via x.colName)
				if type(colName) is str:
					colName_attr = colName.split()[0].strip()
					self.__dict__[colName_attr] = self.data[i]
			except IndexError:
				pass
		self.colNames = columnNames
		
	def SetAltColumns(self, columnNames):
		"""Define an additional set of column names (dictionary keys pointing
		to columns within the data array) for all columns.
		Does not erase previous column-name definitions.
		"""
		for i in range(self.nCols):
			try:
				colName = columnNames[i]
				self.dict[colName] = self.data[i]
				# define a new attribute, if possible (for access via x.colName)
				if type(colName) is str:
					colName_attr = colName.split()[0].strip()
					self.__dict__[colName_attr] = self.data[i]
			except IndexError:
				pass

	def AddColumnName(self, oldName, newName):
		if (type(newName) is not str):
			msg = "New columns names must be strings."
			raise KeyError(msg)
		if (newName in self.colNames):
			msg = "%s is already a column name in this ListDataFrame." % newName
			raise KeyError(msg)
		if (oldName in self.colNames):
			column = self.dict[oldName]
			self.dict[newName] = self.dict[oldName]
			colName_attr = newName.split()[0].strip()
			self.__dict__[colName_attr] = column
		else:
			msg = "Column name \"%s\" does not exist." % oldName
			raise KeyError(msg)

	def ChangeColumnName(self, oldName, newName):
		"""Change the name of one of the columns.  Change is propagated into
		the internal attribute dictionary, so obj.newName will return the
		column which obj.oldName formerly returned.
		"""
		if (oldName in self.colNames):
			# replace name in column name list
			newList = self.colNames[:]
			i_old = newList.index(oldName)
			newList.insert(i_old, newName)
			newList.remove(oldName)
			# store new column names, generate keys and attributes
			self.SetColumns(newList)
			# clean up internal dictionary by removing old attribute ref
			oldName_attr = oldName.split()[0].strip()
			if oldName in self.__dict__:
				junk = self.__dict__.pop(oldName_attr)
		else:
			msg = "Column name \"%s\" does not exist." % oldName
			raise KeyError(msg)

	def AddNewColumn(self, dataColumn, columnName=None):
		"""Adds a new column to the ListDataFrame, along with the column name,
		if supplied. Throws an error if dataColumn is not a list or numpy array;
		also throws an error if the length of dataColumns is different from
		the existing columns.
		"""
		if type(dataColumn) not in [list, np.ndarray]:
			raise TypeError(error1)
		if len(dataColumn) != len(self.data[0]):
			raise TypeError(error2)

		self.data.append(dataColumn)
		self.nCols += 1
		if columnName is not None and self.colNames is not None:
			columnNames = copy.copy(self.colNames)
			columnNames.append(columnName)
			self.SetColumns(columnNames)			
	

		
	
		
class ArrayDataFrame(object):
	"""A class designed to hold a 2D NumPy floating-point array, and 
	optionally a list of column names for the array.  When indexed 
	with one of the column names (e.g., obj["radius"]), it acts like a 
	dictionary and returns the corresponding column.  When indexed with
	an integer or a slice, it acts like the underlying NumPy array.
	
	If the column names are strings, then they also become attributes
	of the object instance and can be accessed as, e.g., obj.radius -- as
	long as the names are valid Python identifiers (must contain only
	alphanumerics or _ and must start with letter or _).
	
	Example: if the first column corresponds to column name "radius", then
	it can be accessed as: obj[:,0], obj["radius"], or obj.radius (and also
	as obj.data[:,0]).
	
	The underlying NumPy array is always accessable as obj.data
	
	If instantiated without a list of column names, it behaves just
	like an ordinary NumPy array (except for being somewhat slower).
	"""

	def __init__(self, array, columnNames=None):
		if type(array) != np.ndarray or len(array.shape) != 2:
			raise TypeError("Input to ArrayDataFrame should be NumPy 2D array")
		self.data = array
		self.colNames = columnNames
		self.dict = {}
		
		arShape = np.shape(array)
		self.nCols = arShape[1]
		if self.colNames is not None:
			self.SetColumns(columnNames)
	
	def __getitem__(self, key):
		"""Defines behavior of indexing: indexing with strings causes
		internal column-name dictionary to be accessed (returns corresponding
		column of data array); indexing with anything else (e.g., integers or
		slices) is passed on to the data array.
		"""
		ktype = type(key)
		if ktype is str:
			return self.dict[key]
		else:
			return self.data[key]
	
	def __str__(self):
		outString = str(self.data)
		if self.colNames is not None:
			outString = str(self.colNames) + "\n" + outString
		return outString
	
	def SetColumns(self, columnNames):
		"""Define the column names (dictionary keys pointing to columns
		within the data array.
		If called more than once, erases previous column-name definitions.
		"""
		if self.dict != {}:
			# remove old column definitions
			for oldName in self.dict:
				# remove old column-name attributes
				oldName_attr = oldName.split()[0].strip()
				if oldName_attr in self.__dict__:
					junk = self.__dict__.pop(oldName_attr)
			self.dict = {}
		for i in range(self.nCols):
			try:
				colName = columnNames[i]
				self.dict[colName] = self.data[:,i]
				# define a new attribute, if possible
				if type(colName) is str:
					colName_attr = colName.split()[0].strip()
					self.__dict__[colName_attr] = self.data[:,i]
			except IndexError:
				pass
		
	def SetAltColumns(self, columnNames):
		"""Define an additional set of column names (dictionary keys pointing
		to columns within the data array).
		Does not erase previous column-name definitions.
		"""
		for i in range(self.nCols):
			try:
				colName = columnNames[i]
				self.dict[colName] = self.data[:,i]
				# define a new attribute, if possible
				if type(colName) is str:
					colName_attr = colName.split()[0].strip()
					self.__dict__[colName_attr] = self.data[:,i]
			except IndexError:
				pass
		
	def ChangeColumnName(self, oldName, newName):
		"""Change the name of one of the columns.  Change is propagated into
		the internal attribute dictionary, so obj.newName will return the
		column which obj.oldName formerly returned.
		"""
		if (oldName in self.colNames):
			# replace name in column name list
			newList = self.colNames[:]
			i_old = newList.index(oldName)
			newList.insert(i_old, newName)
			newList.remove(oldName)
			# store new column names, generate keys and attributes
			self.SetColumns(newList)
			# clean up internal dictionary by removing old attribute ref
			oldName_attr = oldName.split()[0].strip()
			if oldName in self.__dict__:
				junk = self.__dict__.pop(oldName_attr)
		else:
			msg = "Column name \"%s\" does not exist." % oldName
			raise KeyError(msg)

		
		

def ReadTableArray(fileName, skip="#", dataFrame=False, delimiter=None):
	"""Read data from fileName, store in a NumPy array.  All values are
	stored as floating-point.  Format is row-major: d[i][j] = d[i,j] =
	row i, column j.  (To access an entire column, use d[:,j].)
	Blank lines are ignored.
	
	skip = string containing one or more characters which.  Lines
	beginning with any of these characters will be ignored.
	
	If dataFrame=True, then the result is an ArrayDataFrame object
	containing the NumPy array.
	"""
	
	# open file in "universal" mode to ensure Mac or DOS/Windows
	# line endings are converted to \n
	lines = open(fileName, 'rU').readlines()
	dlines = [line.rstrip() for line in lines if len(line.strip()) > 0 and line[0] not in skip ]
	
	nrows = len(dlines)
	ncols = len(dlines[0].split(delimiter))
	dataArray = np.zeros((nrows, ncols))
	
	for i in range(nrows):
		pieces = dlines[i].split(delimiter)
		for j in range(ncols):
			dataArray[i, j] = float(pieces[j])
	
	if dataFrame:
		return ArrayDataFrame(dataArray)
	else:
		return dataArray



def ExtractSubLists( textList, nSubLists ):
	"""Given a list of strings, where each string is of the
	form "{x1, ..., xn}" with n = nSubLists elements, return
	a list contaning nSubLists NumPy arrays (1-D).
	"""
	bigList = []
	for i in range(nSubLists):
		bigList.append([])
	for textChunk in textList:
		bareText = textChunk.strip().strip("{").strip("}")
		pp = bareText.split(",")
		for i in range(nSubLists):
			bigList[i].append(float(pp[i]))
	for i in range(nSubLists):
		bigList[i] = np.array(bigList[i])
	
	return bigList


def InsertAndReplace( theList, ii, newItems ):
	"""Given a list, replace the entry at index ii with the elements of
	newItems (also a list).
	"""
	nNewItems = len(newItems)
	if (ii < 0) or (ii > len(theList)):
		msg = "\ndatautils.InsertAndReplace: *** ERROR: requested insert location"
		msg += " (index = %d) is < 0 or > length(theList) [%d]" % (ii, len(theList))
		msg += "\n"
		print(msg)
		return
	del theList[ii]
	for j in reversed(range(nNewItems)): theList.insert(ii, newItems[j])


def AddExtraColumnNames( columnNames, subListColumns, subListLengths, subListSuffixes ):
	"""Given a list of column names, process it to replace column names for those
	columns which have sub-lists. New column names corresponding to each sub-list
	column are inserted in place of the original name, for each such column.
	"""
	oldColNames = [ columnNames[i] for i in subListColumns ]
	nSubListCols = len(subListColumns)

	for i in range(nSubListCols):
		baseName = oldColNames[i]
		nSubLists = subListLengths[i]
		# generate suffixes:
		if (subListSuffixes is not None):
			if (len(subListSuffixes) != nSubLists):
				msg = "\tdatautils.AddExtraColumnNames: *** WARNING: number of subListSuffixes"
				msg += " elements (%d) != actual number\n\tof sub-lists (%d)" % (len(subListSuffixes), nSubLists)
				msg += " for column with orig. name = %s...\n" % (baseName)
				msg += "\tNumerical suffixes will be used instead for new column names.\n"
				print(msg)
				suffixes = [ str(k) for k in range(nSubLists) ]
			else:
				suffixes = subListSuffixes
		else:
			suffixes = [ str(k) for k in range(nSubLists) ]
		newNames = [ "%s_%s" % (baseName, suffixes[k]) for k in range(nSubLists) ]
		insertLoc = columnNames.index(baseName)
		InsertAndReplace(columnNames, insertLoc, newNames)


def ColumnToFloats( inputList, blankValue ):
	"""Takes a list of numbers in string format and converts them to floating-point,
	with blank entries being replaced by blankValue (which should be float).
	"""
	try:
		floatList = np.array(inputList, "Float64")
	except ValueError:
		# looks like column has some blanks in it
		floatList = copy.copy(inputList)
		for j in range(len(inputList)):
			try:
				floatList[j] = float(inputList[j])
			except ValueError:
				floatList[j] = blankValue
		floatList = np.array(floatList)
	return floatList


def ReadCompositeTable( fileName, skip="#", delimiter=None, noConvert=None,
			intCols=None, blankVal=0, convertSubLists=False, expandSubLists=False, 
			dataFrame=False, columnRow=None, subListSuffixes=None ):
	"""Function which reads a text datafile and returns a list of columns.
	Comments and other lines to skip should start with the "skip" character
	(which by default is "#"); column separators are specified with "delimiter"
	(default is whitespace).
	   By default, all columns are converted to 1-D NumPy arrays, unless
	the data in that column are non-numeric [only the first row of data is
	checked to see which columns might be non-numeric] or the column number
	[0-based: first column = 0, 2nd column = 1, etc.] is in the noConvert list.
	   Numeric columns with column number in intCols (list) are converted to Int64 arrays;
	all other numeric columns become Float64 arrays.
	   blankVal specifies the default number to use for blank values in numerical
	columns.
	   convertSubLists specifies whether embedded sublists (e.g., "{x,y,z}" should be
	recognized and processed; if so, each such column becomes a *list of NumPy arrays*;
	if convertSubLists=False, then each such column is a list of strings.
	   If expandSublists=True, then embedded sublists are converted into extra
	columns (this forces convertSubLists to be True).
	   If dataFrame=True, then the result is a ListDataFrame object.
	   If columnRow = x, then that line [0-based; first line = 0, etc.] is assumed
	to contain column headers and is processed accordingly (only useful if
	dataFrame = True as well).
	   In addition, if columnRow != None, then subListSuffixes can be used to 
	modify the column names for sublists (newNames[i] = origName + "_" + subListSuffixes[i]);
	if subListSuffixes is None [the default], then renamed column names have 
	"_0", "_1", etc. as suffixes.
	"""
	
	subListsFound = False
	
	if noConvert is None:
		noConvert = []
	if intCols is None:
		intCols = []
	if expandSubLists is True:
		convertSubLists = True
	if convertSubLists is True:
		subListCols = []
		subListLengths = {}
		subListLengthList = []
		
	nDataRows = CountDataLinesInFile(fileName, skip=skip)
	nAllRows = CountLinesInFile(fileName)

	# open file in "universal" mode to convert Mac or DOS line endings to \n
	inFile = open(fileName, 'rU')
	dlines = [line.rstrip() for line in inFile if len(line.strip()) > 0 and line[0] not in skip ]
	
	# if requested, extract column names
	if ((columnRow is not None) and (columnRow >= 0) and (columnRow < nAllRows)):
		inFile.seek(0,0)   # rewind to beginning of file
		i = 0
		while (i <= columnRow):
			line = inFile.readline()
			i += 1
		colHeaderLine = line.strip("#")
		pp = colHeaderLine.split(delimiter)
		colNames = [ p.strip() for p in pp ]
	else:
		colNames = None
	
	inFile.close()
	
	
	# Figure out number of columns, which ones are non-numeric, and which have
	# sub-lists (if we're allowing for the latter)
	pp = dlines[0].split(delimiter)
	nInputCols = len(pp)
	nonNumberCols = []
	for i in range(nInputCols):
		if (i not in intCols) and (i not in noConvert):
			# check to make sure this column has numbers
			try:
				x = float(pp[i])
			except ValueError:
				if convertSubLists is True and pp[i].find("{") >= 0:
					# a-ha, this is a column with sublists, so let's convert it
					subListsFound = True
					subListCols.append(i)
					ppp = pp[i].split(",")
					nSubLists = len(ppp)
					subListLengths[i] = nSubLists
					subListLengthList.append(nSubLists)
				else:
					noConvert.append(i)
	
	
	# Create the master list of input columns
	dataList = []
	for i in range(nInputCols):
		dataList.append([])
	# go through the table and assign entries to individual-column lists
	for n in range(nDataRows):
		pieces = dlines[n].split(delimiter)
		for i in range(nInputCols):
			dataList[i].append(pieces[i])
	
	
	# Now convert columns to NumPy arrays, if possible:
	if (not expandSubLists):
		# "Normal" approach (if sublists columns exist, then each is stored 
		# as a list of NumPy arrays); total number of columns is unchanged.
		# Note that columns in noConvert are left untouched (as list of strings)
		for i in range(nInputCols):
			if i in intCols:
				dataList[i] = np.array(dataList[i], "Int64")
			elif convertSubLists is True and i in subListCols:
				dataList[i] = ExtractSubLists(dataList[i], subListLengths[i])
			elif i not in noConvert:
				# this must, by default, be a floating-point column
				dataList[i] = ColumnToFloats(dataList[i], blankVal)
	else:
		# Alternate approach, where we expand sublists into individual, new columns.
		# Have to be careful, since number of columns in dataList will be changing...
		# Note that columns in noConvert are left untouched (as list of strings)
		nAddedCols = 0
		for i_orig in range(nInputCols):  # i_orig = index into original (input) columns
			ii = i_orig + nAddedCols   # ii = index into current version of dataList
			if i_orig in intCols:
				dataList[ii] = np.array(dataList[ii], "Int64")
			elif i_orig in subListCols:
				# number of added cols = n(subLists) - 1, bcs. we *remove* original column
				nAddedCols += subListLengths[i_orig] - 1
				listOfSublists = ExtractSubLists(dataList[ii], subListLengths[i_orig])
				InsertAndReplace(dataList, ii, listOfSublists)
			elif i_orig not in noConvert:
				# this must, by default, be a floating-point column
				dataList[ii] = ColumnToFloats(dataList[ii], blankVal)
	
	
	# OK, if there were sublists *and* we generated extra columns, update
	# the colNames list to account for extra columns
	if (expandSubLists is True) and (subListsFound is True) and (colNames is not None):
		AddExtraColumnNames(colNames, subListCols, subListLengthList, subListSuffixes)

	if dataFrame:
		return ListDataFrame(dataList, colNames)
	else:
		return dataList


def ReadCompositeTableFromText( textLines, skip="#", delimiter=None, noConvert=None,
			intCols=None, blankVal=0, convertSubLists=False, expandSubLists=False, 
			dataFrame=False, columnRow=None, subListSuffixes=None ):
	"""Identical to ReadCompositeTable, except that it accepts a list of lines
	(each line a string), with the first line assumed to be column headers.
	"""
	subListsFound = False
	
	if noConvert is None:
		noConvert = []
	if intCols is None:
		intCols = []
	if expandSubLists is True:
		convertSubLists = True
	if convertSubLists is True:
		subListCols = []
		subListLengths = {}
		subListLengthList = []
		
	nAllRows = len(textLines)
	dlines = [line.rstrip() for line in textLines if len(line.strip()) > 0 and line[0] not in skip ]
	nDataRows = len(dlines)
	
	# if requested, extract column names
	if ((columnRow is not None) and (columnRow >= 0) and (columnRow < nAllRows)):
		colHeaderLine = textLines[columnRow].strip(skip)
		colNames = [ p.strip() for p in colHeaderLine.split(delimiter) ]
	else:
		colNames = None
	
	# Figure out number of columns, which ones are non-numeric, and which have
	# sub-lists (if we're allowing for the latter)
	pp = dlines[0].split(delimiter)
	nInputCols = len(pp)
	nonNumberCols = []
	for i in range(nInputCols):
		if (i not in intCols) and (i not in noConvert):
			# check to make sure this column has numbers
			try:
				x = float(pp[i])
			except ValueError:
				if convertSubLists is True and pp[i].find("{") >= 0:
					# a-ha, this is a column with sublists, so let's convert it
					subListsFound = True
					subListCols.append(i)
					ppp = pp[i].split(",")
					nSubLists = len(ppp)
					subListLengths[i] = nSubLists
					subListLengthList.append(nSubLists)
				else:
					noConvert.append(i)
	
	
	# Create the master list of input columns
	dataList = []
	for i in range(nInputCols):
		dataList.append([])
	# go through the table and assign entries to individual-column lists
	for n in range(nDataRows):
		pieces = dlines[n].split(delimiter)
		for i in range(nInputCols):
			dataList[i].append(pieces[i])
	
	
	# Now convert columns to NumPy arrays, if possible:
	if (not expandSubLists):
		# "Normal" approach (if sublists columns exist, then each is stored 
		# as a list of NumPy arrays); total number of columns is unchanged.
		# Note that columns in noConvert are left untouched (as list of strings)
		for i in range(nInputCols):
			if i in intCols:
				dataList[i] = np.array(dataList[i], "Int64")
			elif convertSubLists is True and i in subListCols:
				dataList[i] = ExtractSubLists(dataList[i], subListLengths[i])
			elif i not in noConvert:
				# this must, by default, be a floating-point column
				dataList[i] = ColumnToFloats(dataList[i], blankVal)
	else:
		# Alternate approach, where we expand sublists into individual, new columns.
		# Have to be careful, since number of columns in dataList will be changing...
		# Note that columns in noConvert are left untouched (as list of strings)
		nAddedCols = 0
		for i_orig in range(nInputCols):  # i_orig = index into original (input) columns
			ii = i_orig + nAddedCols   # ii = index into current version of dataList
			if i_orig in intCols:
				dataList[ii] = np.array(dataList[ii], "Int64")
			elif i_orig in subListCols:
				# number of added cols = n(subLists) - 1, bcs. we *remove* original column
				nAddedCols += subListLengths[i_orig] - 1
				listOfSublists = ExtractSubLists(dataList[ii], subListLengths[i_orig])
				InsertAndReplace(dataList, ii, listOfSublists)
			elif i_orig not in noConvert:
				# this must, by default, be a floating-point column
				dataList[ii] = ColumnToFloats(dataList[ii], blankVal)
	
	
	# OK, if there were sublists *and* we generated extra columns, update
	# the colNames list to account for extra columns
	if (expandSubLists is True) and (subListsFound is True) and (colNames is not None):
		AddExtraColumnNames(colNames, subListCols, subListLengthList, subListSuffixes)

	if dataFrame:
		return ListDataFrame(dataList, colNames)
	else:
		return dataList


