# ncgmp09_ValidateDatabase.py  
#   Python script to inventory tables, feature datasets
#   and feature classes in a geodatabase and to check
#   for conformance with NCGMP09 geodatabase schema.
#   For more information, see tail of this file. 
#   Assumes ArcGIS 10 or higher.
#   Ralph Haugerud, USGS
#
#   Takes two arguments: <geodatabaseName> <outputWorkspace>
#     and writes a file named <geodatabaseName>-NCGMP09conformance.txt.
#   At present only works on a geodatabase in the local directory.
#   Requires that ncgmp09_definition.py be present in the local directory 
#     or in the appropriate Python library directory.
#   Incomplete error trapping and no input checking. 
#
# NOTE: THIS CODE HAS NOT BEEN THOROUGHLY TESTED
#   If you find problems, or think you see errors, please let me know.
#   Zip up the database, the conformance report (if one is written), 
#   a brief discussion of what's wrong, and email zip file to me at
#   	rhaugerud@usgs.gov
#   Please include "NCGMP09" in the subject line.
#   Thanks!

print '  importing arcpy...'
import arcpy, sys, time, os.path
from NCGMP09v1.1_Definition import tableDict 

versionString = 'NCGMP09v1.1-ValidateDatabase-Arc10.0.py, version of 22 May 2012'

debug = True

# fields we don't want listed or described when inventorying dataset:
standardFields = ('OBJECTID','SHAPE','Shape','SHAPE_Length','SHAPE_Area','ZOrder',
                  'AnnotationClassID','Status','TextString','FontName','FontSize','Bold',
                  'Italic','Underline','VerticalAlignment','HorizontalAlignment',
                  'XOffset','YOffset','Angle','FontLeading','WordSpacing','CharacterWidth',
			'CharacterSpacing','FlipAngle','Override','Shape_Length','Shape_Area') 

# fields whose values must be defined in Glossary
gFieldDefList = ('Type','TypeModifier','LocationMethod','Lithology','ProportionTerm','TimeScale',
                 'Qualifier','Property','ExistenceConfidence','IdentityConfidence',
                 'ScientificConfidence','ParagraphStyle','AgeUnits','GeneralLithology',
                 'GeneralLithologyConfidence')

tables = []
fdsfc = []
all_IDs = []		# list of should-be unique identifiers
allMapUnitRefs = []	# list of MapUnit references (from various Poly feature data sets)
allGlossaryRefs = []	# list of all references to Glossary
allDataSourcesRefs = [] # list of all references to DataSources
allBadNulls = ["""  Pseudonulls (value = <space>) commonly result from loading empty data into
  string fields in which nulls are not allowed. Trailing spaces are commonly
  produced by hand-correction of pseudonulls. The following fields contain
  pseudonulls or trailing spaces"""]

gdbDescription = []
schemaErrors = []
schemaExtensions = []

duplicateIDs = []
unreferencedIds = ['  OwnerIDs and ValueLinkIDs in ExtendedAttributes that are absent elsewhere in the database']
extendedAttribIDs = []
missingSourceIDs = ['  Missing DataSources entries. Only one reference to each missing source is cited']
unusedDataSources = ['  Entries in DataSources that are not otherwise referenced in database']
dataSourcesIDs = []
missingDmuMapUnits = ['  MapUnits missing from DMU. Only one reference to each missing unit is cited']
missingStandardLithMapUnits = ['  MapUnits missing from StandardLithology. Only one reference to each missing unit is cited']
unreferencedDmuMapUnits = ['  MapUnits in DMU that are not present on map or in CMU']
unreferencedStandardLithMapUnits = ['  MapUnits in StandardLithology that are not present on map']
equivalenceErrors = ['  Units present in map, DMU, CMU, and cross sections']
dmuMapUnits = []
cmuMapUnits = []
gmapMapUnits = []
csMapUnits = []
standardLithMapUnits = []
missingGlossaryTerms = ['  Missing terms in Glossary. Only one reference to each missing term is cited']
unusedGlossaryTerms = ['  Terms in Glossary that are not otherwise used in geodatabase']
glossaryTerms = []
unusedGeologicEvents = ['  Events in GeologicEvents that are not cited in ExtendedAttributes']
hKeyErrors = ['  HierarchyKey errors, DescriptionOfMapUnits']

def addMsgAndPrint(msg, severity=0): 
	# prints msg to screen and adds msg to the geoprocessor (in case this is run as a tool) 
	# print msg 
	try: 
	  for string in msg.split('\n'): 
		# Add appropriate geoprocessing message 
		if severity == 0: 
			arcpy.AddMessage(string) 
		elif severity == 1: 
			arcpy.AddWarning(string) 
		elif severity == 2: 
			arcpy.AddError(string) 
	except: 
		pass 

def writeContentErrors(outfl,errors,noErrorString):
    if len(errors) == 1:
        outfl.write('  '+noErrorString+'\n\n')
    else:
        outfl.write(errors[0]+'\n')
        # drop first line
        errors2 = errors[1:]
        # find duplicates
        errors2.sort()
        errors3 = []
        i = 0
        n = 1
        oldLine = errors2[0]
        for i in range(1,len(errors2)):
            if errors2[i] == oldLine:
                n = n+1
            else:
                errors3.append([oldLine,n])
                oldLine = errors2[i]
                n = 1
        # write results
        for aline in errors3:
            outfl.write(aline[0])
            if aline[1] > 1:
                outfl.write('--'+str(aline[1]+1)+' duplicates\n')
            else:
                outfl.write('\n')
        outfl.write('\n')

def listDataSet(dataSet):
	addMsgAndPrint('    '+dataSet)
	startTime = time.time()
	nrows = arcpy.GetCount_management(dataSet)
	elapsedTime = time.time() - startTime
	if debug: addMsgAndPrint('      '+str(nrows)+' rows '+ "%.1f" % elapsedTime +' sec')
	gdbDescription.append('    '+dataSet+', '+str(nrows)+' records')
        startTime = time.time()
	fields = arcpy.ListFields(dataSet)
	elapsedTime = time.time() - startTime
	if debug: addMsgAndPrint('      '+str(len(fields))+' fields '+ "%.1f" % elapsedTime +' sec')
	for field in fields:
	   if not (field.name in standardFields):
		gdbDescription.append('      '+field.name+' '+field.type+':'+str(field.length)+'  '+str(field.required))

def checkMapFeatureClasses(fds,prefix,fcs):
	addMsgAndPrint('  Checking for required feature classes...')
	requiredFeatureClasses = []
	for fc in ['ContactsAndFaults','MapUnitPolys','DataSourcePolys']:
		requiredFeatureClasses.append(prefix+fc)
	for fc in requiredFeatureClasses:
		if not (fc in fcs): 
			schemaErrors.append('Feature data set '+fds+', feature class '+fc+' is missing')

def checkTableFields(dBTable,defTable):
	dBtable = str(dBTable)
	# build dictionary of required fields 
	requiredFields = {}
	requiredFieldDefs = tableDict[defTable]
	for fieldDef in requiredFieldDefs:
		requiredFields[fieldDef[0]] = fieldDef
	# build dictionary of existing fields 
	existingFields = {}
	fields = arcpy.ListFields(dBtable)
	for field in fields:
		existingFields[field.name] = field
	# now check to see what is excess / missing
	for field in requiredFields.keys():
	   if field not in existingFields:
		schemaErrors.append(dBTable+', field '+field+' is missing')
	for field in existingFields.keys():
	   if not (field in standardFields) and not (field in requiredFields):
		schemaExtensions.append(dBTable+', field '+field+' is not required')
	   # check field definition
	   if field in requiredFields.keys():
		# field type
		if existingFields[field].type <> requiredFields[field][1]:
			schemaErrors.append(dBTable+', field '+field+', type should be '+requiredFields[field][1])
		# field nullable?
		if existingFields[field].isNullable:
			nullStatus = 'NullsOK'
		else:
			nullStatus = 'NoNulls'
		if nullStatus <> requiredFields[field][2]:
			schemaErrors.append(dBTable+', field '+field+' should be '+requiredFields[field][2])

def loadTableValues(tableName,fieldName,valueList):
	try:
		rows = arcpy.SearchCursor(tableName,'','',fieldName)
	except:
		loadValuesFlag = False
	else: 
		row = rows.next()
		while row:
			if row.getValue(fieldName) <> None:
				valueList.append(row.getValue(fieldName))
			row = rows.next() 
		loadValuesFlag = True
	return loadValuesFlag

def inventoryValues(thisDatabase,table):
	# build list of fields in this table that must have values defined in Glossary
	# build list of fields that point at DataSources (name cn 'Source'
	# note if MapUnit field is present
	# calculate value of _ID field
	tableFields = arcpy.ListFields(table)
	fields = []
	mapUnitExists = False
	if debug: addMsgAndPrint('      Listing fields')
	for field in tableFields:
		fields.append(field.name)
		if field.name == 'MapUnit':
			mapUnitExists = True
	glossFields = []
	sourceFields = []
	idField = table+'_ID'
	hasIdField = False
	if debug: addMsgAndPrint('      Getting glossary and source fields')
	for field in fields:
		if field in gFieldDefList:
			glossFields.append(field)
		if field.find('Source') >= 0 and field.find('_ID') < 0 and table <> 'DataSources':
			sourceFields.append(field)
		if field == idField:
			hasIdField = True
	# get rows from table of interest
	if debug: addMsgAndPrint('      Getting rows')
	try:
	    rows = arcpy.SearchCursor(thisDatabase+'/'+table)
	except:
            addMsgAndPrint('failed to set rows')
	# step through rows and inventory values in specified fields
	row = rows.next()
	while row:
		if hasIdField:
			all_IDs.append([row.getValue(idField),table])
		if table <> 'Glossary':
			for field in glossFields:
			  try:
				if row.getValue(field) <> '' and row.getValue(field) <> None:
                                    allGlossaryRefs.append([str(row.getValue(field)),field,table])
			  except:
				errString = 'Table '+table+', OBJECTID = '+str(row.getValue('OBJECTID'))
				errString = errString+', field '+field+' caused an error'
				addMsgAndPrint(errString)
				addMsgAndPrint('Field value is <'+str(row.getValue(field))+'>')
				pass
		if mapUnitExists:
                        mu = str(row.getValue('MapUnit'))
                        if mu <> '':
                                if table <> 'DescriptionOfMapUnits' and table <> 'StandardLithology':
                                        allMapUnitRefs.append([mu,table])
                                if table == 'MapUnitPolys':
                                        gmapMapUnits.append(mu)
                                if table[0:2] == 'CS' and table[3:] == 'MapUnitPolys':
                                        csMapUnits.append(mu)                                       
                                if table == 'CMUMapUnitPolys' or table == 'CMUMapUnitPoints':
                                        cmuMapUnits.append(mu)
                                if table == 'DescriptionOfMapUnits':
                                        if mu <> 'None':
                                                dmuMapUnits.append(mu)
                                        
		for field in sourceFields:
                    try:
			allDataSourcesRefs.append([row.getValue(field),field,table])
		    except:
                        addMsgAndPrint('Failed to append to allDataSourcesRefs:')
                        addMsgAndPrint('  table '+table+', field = '+str(field))
		# check for pseudonulls and trailing spaces
		try:
		  tableRow = '    Table '+table+',row OBJECTID='+str(row.getValue('OBJECTID'))+', field'
		  badNull = False
		  for field in tableFields:
			if field.type == 'String' and not field.IsNullable:
			   #print table+'  '+field.name
			   if row.getValue(field.name)[-1:] == ' ':
				tableRow = tableRow+' '+field.name
				badNull = True
		  if badNull:
			allBadNulls.append(tableRow)
		except:
		  pass
		row = rows.next()
	addMsgAndPrint('      Finished '+table)
			
def inventoryWorkspace(tables,fdsfc):
	addMsgAndPrint('  Inventorying geodatabase...')
	featureDataSets = arcpy.ListDatasets()
	gdbDescription.append('Tables: ')
	for table in tables:
		listDataSet(table)
	for featureDataSet in featureDataSets:
		gdbDescription.append('Feature data set: '+featureDataSet)
		arcpy.env.workspace = thisDatabase
		arcpy.env.workspace = featureDataSet
		featureClasses = arcpy.ListFeatureClasses()
		featureClassList = []
		for featureClass in featureClasses:
			listDataSet(featureClass)
			featureClassList.append(featureClass)
		fdsfc.append([featureDataSet,featureClassList])

def checkFieldsAndFieldDefinitions():
	addMsgAndPrint( '  Checking fields and field definitions, inventorying special fields...')
	for table in tables:
            if debug: addMsgAndPrint('    Table = '+table)
            arcpy.env.workspace = thisDatabase
            if not tableDict.has_key(table): 
                schemaExtensions.append('Table '+table+' is not required')
            else: 
                checkTableFields(table,table)
            inventoryValues(thisDatabase,table)
	for fds in fdsfc:
            if not fds[0] in ('GeologicMap','CorrelationOfMapUnits') and fds[0:12] <> 'CrossSection':
                schemaExtensions.append('Feature dataset '+fds[0]+' is not required')
            arcpy.env.workspace = thisDatabase
            arcpy.env.workspace = fds[0]
            for featureClass in fds[1]:
                if debug: addMsgAndPrint('    Feature class = '+featureClass)
                if not tableDict.has_key(featureClass): 
                    schemaExtensions.append('Feature class '+featureClass+' is not required')
                else: 
                    checkTableFields(featureClass,featureClass)
                inventoryValues(thisDatabase,featureClass)

def checkRequiredElements():
	addMsgAndPrint( '  Checking for required elements...')
	requiredFeatureDataSets = ['GeologicMap']
	requiredTables = ['DescriptionOfMapUnits','Glossary','DataSources']
	for tb1 in requiredTables:
		isPresent = False
		for tb2 in tables:
			if tb1 == tb2:
				isPresent = True
		if not isPresent:
			schemaErrors.append('Table '+tb1+' is missing')
	for fds1 in requiredFeatureDataSets:
		isPresent = False
		for fds2 in fdsfc:
			if fds2[0] == fds1: 
				isPresent = True
		if not isPresent:
			schemaErrors.append('Feature data set '+fds1+' is missing')
	for xx in fdsfc:
		fds = xx[0]
		fcs = xx[1]
		if fds[0:12] == 'CrossSection':
			checkMapFeatureClasses(fds,'CS'+fds[12:],fcs)
		if fds == 'GeologicMap':
			checkMapFeatureClasses(fds,'',fcs)
		if fds == 'CorrelationOfMapUnits':
			if not ('CMULines' in fcs):
				schemaErrors.append('Feature data set '+fds+', feature class CMULines is missing')
			if not ('CMUMapUnitPolys' in fcs):
				schemaErrors.append('Feature data set '+fds+', feature class CMUMapUnitPolys is missing')
			if not ('CMUText' in fcs):
				schemaErrors.append('Feature data set '+fds+', feature class CMUText is missing')

def checkContent():
	addMsgAndPrint( '  Checking content...')
	arcpy.env.workspace = thisDatabase
	# Check for uniqueness of _ID values
	addMsgAndPrint('    Checking uniqueness of ID values')
	all_IDs.sort()
	duplicateIDs.append('  Duplicate _ID values')
	for n in range(1,len(all_IDs)):
		if all_IDs[n-1][0] == all_IDs[n][0]:
			duplicateIDs.append('    '+all_IDs[n][0]+', tables '+all_IDs[n-1][1]+' '+all_IDs[n][1])
	# Check for OwnerIDs and ValueLinkIDs in ExtendedAttributes that don't match an existing _ID
	if not loadTableValues('ExtendedAttributes','OwnerID',extendedAttribIDs):
		unreferencedIds.append('    Error: did not find field OwnerID in table ExtendedAttributes')
	if not loadTableValues('ExtendedAttributes','ValueLinkID',extendedAttribIDs):
		unreferencedIds.append('    Error: did not find field ValueLinkID in table ExtendedAttributes')
	#compare
	extendedAttribIDs.sort()
	all_IDs0 = []
	for id in all_IDs:
		all_IDs0.append(str(id[0]))
	for id in extendedAttribIDs:
		if id <> None and not id in all_IDs0:
			unreferencedIds.append('    '+id)
	# Check allDataSourcesRefs against DataSources
	addMsgAndPrint('    Comparing DataSources_IDs with DataSources')	
	if loadTableValues('DataSources','DataSources_ID',dataSourcesIDs):
		# compare 
		allDataSourcesRefs.sort()
		lastID = ''
		for id in allDataSourcesRefs:
			if id[0] <> None and id[0] <> lastID:
				lastID = id[0]
				if id[0] not in dataSourcesIDs:
					missingSourceIDs.append('    '+id[0]+', cited in field '+id[1]+' table '+id[2])
		# compare other way
		allSourceRefIDs = []
		for ref in allDataSourcesRefs:
			allSourceRefIDs.append(ref[0])
		for id in dataSourcesIDs:
			if not id in allSourceRefIDs:
				unusedDataSources.append('    '+id)
	else:
		missingSourceIDs.append('    Error: did not find field DataSources_ID in table DataSources')
		unusedDataSources.append('    Error: did not find field DataSources_ID in table DataSources')
	# Check MapUnits against DescriptionOfMapUnits and StandardLithology
	addMsgAndPrint('    checking MapUnits against DMU and StandardLithology')
	if not loadTableValues('DescriptionOfMapUnits','MapUnit',dmuMapUnits):
		missingDmuMapUnits.append('    Error: did not find field MapUnit in table DescriptionOfMapUnits')
		unreferencedDmuMapUnits.append('    Error: did not find field MapUnit in table DescriptionOfMapUnits')
	if not loadTableValues('StandardLithology','MapUnit',standardLithMapUnits):
		missingStandardLithMapUnits.append('    Error: did not find field MapUnit in table StandardLithology') 
		unreferencedStandardLithMapUnits.append('    Error: did not find field MapUnit in table StandardLithology')
	# compare 
	allMapUnitRefs.sort()
	lastMU = ''
	allMapUnitRefs2 = []
	addMsgAndPrint('    Checking for missing map units in DMU and StandardLithology')
	for mu in allMapUnitRefs:
            if mu[0] <> lastMU:
                lastMU = mu[0]
                allMapUnitRefs2.append(lastMU)
                if mu[0] not in dmuMapUnits:
                    missingDmuMapUnits.append('    '+str(mu[0])+', cited in '+str(mu[1]))
                if mu[0] not in standardLithMapUnits:
                    missingStandardLithMapUnits.append('    '+str(mu[0])+', cited in '+str(mu[1]))
        # compare map, DMU, CMU, and cross-sections
        addMsgAndPrint('    Comparing units present in map, DMU, CMU, and cross sections')
        dmuMapUnits2 = list(set(dmuMapUnits))
        cmuMapUnits2 = list(set(cmuMapUnits))
        gmapMapUnits2 = list(set(gmapMapUnits))
        csMapUnits2 = list(set(csMapUnits))
        allMapUnits = []
        muSets = [gmapMapUnits,dmuMapUnits,cmuMapUnits2,csMapUnits2]
        for muSet in muSets:
            for mu in muSet:
                if not mu in allMapUnits:
                    allMapUnits.append(mu)
        allMapUnits.sort()
        #                         1234567890123456789012345678901234567890
        equivalenceErrors.append('    Unit       Map  DMU  CMU  XS')
        for mu in allMapUnits:
            line = '    '+mu.ljust(10)
            for muSet in muSets:
                if mu in muSet:
                    line = line+'  X  '
                else:
                    line = line+' --- '
            equivalenceErrors.append(line)
                
        
	# look for excess map units in StandardLithology
	addMsgAndPrint('    Checking for excess map units in StandardLithology')
	lastMu = ''
	standardLithMapUnits.sort()
	for mu in standardLithMapUnits:
		if mu <> lastMu and not mu in allMapUnitRefs2:
			lastMu = mu
			unreferencedStandardLithMapUnits.append('    '+mu)
	# look for unreferenced map units in DMU
	addMsgAndPrint('    Checking for excess map units in DMU')
	for mu in dmuMapUnits:
		if mu not in allMapUnitRefs2 and mu <> '':
			unreferencedDmuMapUnits.append('    '+mu)
	# Check allGlossaryRefs against Glossary
	addMsgAndPrint('    Checking glossary references')
	if loadTableValues('Glossary','Term',glossaryTerms):
		# compare 
		allGlossaryRefs.sort()
		lastTerm = ''
		for term in allGlossaryRefs:
			if str(term[0]) <> 'None' and term[0] <> lastTerm:
				lastTerm = term[0]
				if term[0] not in glossaryTerms:
					if len(term[0]) < 40:
						thisTerm = term[0]
					else:
						thisTerm = term[0][0:37]+'...'
					missingGlossaryTerms.append('    '+thisTerm+', cited in field '+term[1]+', table '+term[2])
		# compare other direction
		glossaryRefs = []
		for ref in allGlossaryRefs:
			glossaryRefs.append(str(ref[0]))
		for term in glossaryTerms:
			if term not in glossaryRefs:
				unusedGlossaryTerms.append('    '+term)
	else:
		missingGlossaryTerms.append('    Error: did not find field Term in table Glossary')
		unusedGlossaryTerms.append('    Error: did not find field Term in table Glossary')
	# Check GeologicEvents against ValueLinkID in ExtendedAttributes
	geologicEvents = []
	if not loadTableValues('GeologicEvents','GeologicEvents_ID',geologicEvents):
		unusedGeologicEvents.append('    Error: did not find field GeologicEvents_ID in table GeologicEvents')
	valueLinks = []
	if not loadTableValues('ExtendedAttributes','ValueLinkID',valueLinks):
		unusedGeologicEvents.append('    Error: did not find field ValueLink in table ExtendedAttributes')
	#compare
	geologicEventRefs = []
	for ve in valueLinks:
		if ve in geologicEvents:
			geologicEventRefs.append(ve)

	# Check formatting of HierarchyKey in DescriptionOfMapUnits
	addMsgAndPrint('    Checking HierarchyKey (DMU) formatting')
	hKeys = []
	if loadTableValues('DescriptionOfMapUnits','HierarchyKey',hKeys):
		partLength = len(hKeys[0].split('-')[0])
		for hKey in hKeys:
			hKeyParts = hKey.split('-')
			keyErr = False
			for hKeyPart in hKeyParts:
				if len(hKeyPart) <> partLength:
					keyErr = True
			if keyErr:
				hKeyErrors.append('    '+hKey)	
	else:
		hKeyErrors.append('    Error: did not find field HierarchyKey in table DescriptionOfMapUnits')

def writeOutput(outFile,tables,thisDatabase):
	addMsgAndPrint( '  Writing output...')
	outfl = open(outFile,'w')
	outfl.write('Geodatabase '+thisDatabase+'\n')
	outfl.write('  Testing for compliance with NCGMP09v1.1 database schema\n')
	outfl.write('  This file written by '+versionString+'\n')
	outfl.write('  '+time.asctime(time.localtime(time.time()))+'\n')
	#  Schema errors
	outfl.write('\n\nSCHEMA ERRORS\n\n')
	if len(schemaErrors) == 0:
		outfl.write('  None\n')
	else: 
		for aline in schemaErrors:
			outfl.write('  '+aline+'\n')
	# Extensions to schema
	outfl.write('\n\nEXTENSIONS TO SCHEMA, may indicate errors\n\n')
	if len(schemaExtensions) == 0:
		outfl.write('  None\n')
	else: 
		for aline in schemaExtensions:
			outfl.write('  '+aline+'\n')
	# Content errors
	outfl.write('\n\nCONTENT ERRORS\n\n')
	writeContentErrors(outfl,duplicateIDs,'No duplicate _IDs')
	writeContentErrors(outfl,missingSourceIDs,'No missing entries in DataSources')
	writeContentErrors(outfl,unusedDataSources,'No unreferenced entries in DataSources')
	writeContentErrors(outfl,missingDmuMapUnits,'No missing MapUnits in DescriptionOfMapUnits')
	writeContentErrors(outfl,equivalenceErrors,'CMU matches DMU matches units on map')
	if 'StandardLithology' in tables:
            writeContentErrors(outfl,missingStandardLithMapUnits,'No missing MapUnits in StandardLithology')
            writeContentErrors(outfl,unreferencedStandardLithMapUnits,'No unreferenced MapUnits in StandardLithology')
	writeContentErrors(outfl,unreferencedDmuMapUnits,'No unreferenced MapUnits in Description of MapUnits')
	writeContentErrors(outfl,missingGlossaryTerms,'No missing terms in Glossary')
	writeContentErrors(outfl,unusedGlossaryTerms,'No unreferenced terms in Glossary')
	if 'ExtendedAttributes' in tables:
	    writeContentErrors(outfl,unreferencedIds,'No rows in ExtendedAttributes that reference nonexistent OwnerIDs or ValueLinkIDs')
	    if 'GeologicEvents' in tables:
                writeContentErrors(outfl,unusedGeologicEvents,'No rows in GeologicEvents not referenced in ExtendedAttributes')
	writeContentErrors(outfl,hKeyErrors,'No format errors in HierarchyKeys')
	writeContentErrors(outfl,allBadNulls,'No pseudonulls or trailing spaces')
	# Database description
	outfl.write('\nGEODATABASE DESCRIPTION\n\n')
	for aline in gdbDescription:
		outfl.write(aline+'\n')
	outfl.close()

def validInputs(thisDatabase,outFile):
	# does input database exist? Is it plausibly a geodatabase?
	if os.path.exists(thisDatabase) and thisDatabase[-4:].lower() in ('.gdb','.mdb'):
		# is output workspace writable?
		try:
			outfl = open(outFile,'w')
			outfl.write('A test')
			outfl.close()
			return True
		except:
			addMsgAndPrint('  Cannot open and write file '+outFile)
			return False
	else:
		addMsgAndPrint('  Object '+thisDatabase+' does not exist or is not a geodatabase')
		return False


thisDatabase = sys.argv[1]
outputWorkspace = sys.argv[2]
addMsgAndPrint('  Starting...')
if not outputWorkspace[-1:] in ('/','\\'):
    outputWorkspace = outputWorkspace+'/'
thisDatabase = os.path.abspath(thisDatabase)
outFile = outputWorkspace + os.path.basename(thisDatabase)+'-conformance.txt'
arcpy.QualifiedFieldNames = False
if validInputs(thisDatabase,outFile):
    try:
        arcpy.env.workspace = thisDatabase
    except:
        addMsgAndPrint('  Unable to load workspace '+thisDatabase+'. Not an ESRI geodatabase?')
    else:
        addMsgAndPrint('  '+versionString)
        addMsgAndPrint('  geodatabase '+thisDatabase+' loaded')
        addMsgAndPrint('  output will be written to file '+outFile)
        tables = list(arcpy.ListTables())
        inventoryWorkspace(tables,fdsfc)
        checkRequiredElements()
        checkFieldsAndFieldDefinitions()
        checkContent()
        writeOutput(outFile,tables,thisDatabase)
        addMsgAndPrint('  DONE')


# Things to be done:
#	Inventory data set   DONE
#	Check for required tables, featuredatasets, featureclasses    DONE 
#	For optional featuredatasets, check for required featureclasses   DONE
#	For required and optional tables, 
#		check for required fields   DONE
#		check field definitions    DONE
# 	Accumulate list of all must-be-globally-unique (_ID) values  DONE
#	Accumulate list of all ToBeDefined values (references to Glossary)   DONE
#	   see gFieldDefList, above
#	   what about StandardLithology:Lithology?
#	Accumulate list of all MapUnit references  DONE
# 	Accumulate list of all DataSources references  DONE
#	Check that must-be-globally-unique values are unique  DONE
#	Check that all values of fields name cn 'Source' correspond to values of DataSources_ID  DONE
#	Check that MapUnits referenced by StandardLithology and any fClass whose name cn 'Poly' 
#		are present in DMU  DONE
#	Check for definitions of ToBeDefined values  DONE
#        EXCEPT PropertyValue values that are numeric (in part)  STILL TO BE DONE!
#	In DMU, check HierarchyKey format  DONE
#	Check for illegal null values: ' ' (null-equivalent) created when loading data into tables  DONE
#	Check that all MapUnits have StandardLithology entries  DONE
#	Check for unreferenced entries in DataSources (DONE), Glossary (DONE), StandardLithology (DONE),
#		DMU (DONE), Geologic Events (DONE),
# 	DOES NOT CHECK THAT GeologicEvents REFERENCED BY ValueLinkID IN ExtendedAttributes ARE PRESENT
#	Error trapping:
#		So it doesn't fail with bad input  DONE, somewhat
#		So it doesn't fail with bad field names. e.g. _ID field  DONE, I think

# check for consistency between CMU, DMU, MapUnitPolys, and any cross-sections:
#     Do units in DMU and CMU match?
#     are all units shown in map and sections listed in CMU and DMU?
#     are all units in DMU present in map and (or) at least one section?
   
