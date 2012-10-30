# ncgmp09v1.1_10.0_CreateDatabase_1.py
#   Python script to create an empty NCGMP09-style
#   ArcGIS 10 geodatabase for geologic map data
#
#   Ralph Haugerud, USGS
#
#   Takes 4 arguments: <outputDir>  <geoDataBaseName> <coordSystem> <number of cross sections>
#     to use local directory, use # for outputDir
#     # accepted for <coordSystem>
#     if geoDatabaseName ends in .gdb, a file geodatabase will be created
#     if geoDatabaseName ends in .mdb, a personal geodatabase will be created
#	coordSystem is a filename for an ESRI coordinate system definition (look 
#	in directory arcgis/Coordinate Systems). Use # to define coordinate system
#     later
#
#   Requires that ncgmp09_definition.py be present in the local directory 
#     or in the appropriate Python library directory.
#
#   On my laptop, this takes many minutes to run and creates a 
#      ~0.5GB file/directory
#
# To use this:
#   	1) run script, e.g.
#		C:\myworkspace> ncgmp09_CreateDatabase.py # newgeodatabase.gdb # 1
#	2) Open newgeodatabase in ArcCatalog, doubleclick on feature data set GeologicMap,
#	   and assign a spatial reference system
#	3) If you use the CorrelationOfMapUnits feature data set, note that you will have to 
#	   manually create the annotation feature class CMUText and add field ParagraphStyle.
#	   (I haven't yet found a way to script the creation of an annotation feature class.)
#	4) If there will be non-standard point feature classes (photos, mineral occurrences,
#	   etc.), copy/paste/rename feature class GenericPoint or GenericSample, as appropriate,
#	   and add necessary fields to new feature class
#	5) Delete any unneeded feature classes and feature data sets
#	6) Load data. Edit as needed
#
#  NOTE: CAN ALSO BE RUN AS TOOLBOX SCRIPT FROM ARCCATALOG

import arcpy, sys, os
from NCGMP09v1_1_Definition import tableDict

versionString = 'NCGMP09v1.1-CreateDatabase-Arc10.0.py, version of 23 February 2012'

default = '#'

#cartoReps = False # False if cartographic representations will not be used

transDict =     { 'String': 'TEXT',
			'Single': 'FLOAT',
			'Double': 'DOUBLE',
			'NoNulls':'NON_NULLABLE',
			'NullsOK':'NULLABLE',
			'Date'  : 'DATE',
			'Integer' : 'LONG',
			'SmallInteger' : 'SHORT',
			'Blob' : 'BLOB'}

usage = """Usage:
   systemprompt> ncgmp09_create.py <directory> <geodatabaseName> <coordSystem>
                <OptionalElements> <#XSections>
   <directory> is existing directory in which new geodatabaseName is to 
      be created, use # for current directory
   <geodatabaseName> is name of gdb to be created, with extension
      .gdb causes a file geodatabase to be created
      .mdb causes a personal geodatabase to be created
   <coordSystem> is a fully-specified ArcGIS coordinate system
   <OptionalElements> is either # or a semicolon-delimited string specifying
      which non-required elements should be created (e.g.,
      OrientationPoints;CartographicLines;RepurposedSymbols )
   <#XSections> is an integer (0, 1, 2, ...) specifying the intended number of
      cross-sections

  Then, in ArcCatalog:
  * If you use the CorrelationOfMapUnits feature data set, note that you will 
    have to manually create the annotation feature class CMUText and add field 
    ParagraphStyle. (I haven't yet found a way to script the creation of an 
    annotation feature class.)
  * If there will be non-standard point feature classes (photos, mineral 
    occurrences, etc.), copy/paste/rename feature class GenericPoint or 
    GenericSample, as appropriate, rename the _ID field, and add necessary
    fields to the new feature class.
  * Delete any unneeded feature classes and feature data sets.
  * Load data, if data already are in GIS form. 
  Edit data as needed.

"""

def addMsgAndPrint(msg, severity=0): 
    # prints msg to screen and adds msg to the geoprocessor (in case this is run as a tool) 
    #print msg 
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

def createFeatureClass(thisDB,featureDataSet,featureClass,shapeType,fieldDefs):
    addMsgAndPrint('    Creating feature class '+featureClass+'...')
    try:
        arcpy.env.workspace = thisDB        
	if featureDataSet == '':
            arcpy.CreateFeatureclass_management(thisDB,featureClass,shapeType)
            thisFC = thisDB + '/' + featureClass
	else:
            arcpy.CreateFeatureclass_management(featureDataSet,featureClass,shapeType)
            thisFC = thisDB+'/'+featureDataSet+'/'+featureClass
            
        for fDef in fieldDefs:
            try:
                if fDef[1] == 'String':
                    arcpy.AddField_management(thisFC,fDef[0],transDict[fDef[1]],'#','#',fDef[3],'#',transDict[fDef[2]])
                else:
                    arcpy.AddField_management(thisFC,fDef[0],transDict[fDef[1]],'#','#','#','#',transDict[fDef[2]])
            except:
                addMsgAndPrint('Failed to add field '+fDef[0]+' to feature class '+featureClass)
                addMsgAndPrint(arcpy.GetMessages(2))
    except:
        addMsgAndPrint(arcpy.GetMessages())
        addMsgAndPrint('Failed to create feature class '+ featureClass +' in dataset '+featureDataSet)
        
        
def main(thisDB,coordSystem,nCrossSections):
	# create feature dataset GeologicMap #
	addMsgAndPrint('  Creating feature dataset GeologicMap...')
	try:
		arcpy.CreateFeatureDataset_management(thisDB,'GeologicMap')
	except:
		addMsgAndPrint(arcpy.GetMessages(2))
	if coordSystem <> '#':
		try:
		    arcpy.DefineProjection_management(thisDB+'/GeologicMap',coordSystem)
		except:
		    addMsgAndPrint(arcpy.GetMessages(2)) 
	
	# create feature classes in GeologicMap
	# poly feature classes
	featureClasses = ['MapUnitPolys']
	for fc in ['OverlayPolys']:
            if fc in OptionalElements:
                featureClasses.append(fc)
	for featureClass in featureClasses:
            fieldDefs = tableDict[featureClass]
            createFeatureClass(thisDB,'GeologicMap',featureClass,'POLYGON',fieldDefs)
                
	# line feature classes
	featureClasses = ['ContactsAndFaults']
	for fc in ['OtherLines']:
            if fc in OptionalElements:
                featureClasses.append(fc)
	for featureClass in featureClasses:
            fieldDefs = tableDict[featureClass]
            createFeatureClass(thisDB,'GeologicMap',featureClass,'POLYLINE',fieldDefs)
            
        # create topology
        addMsgAndPrint('  Creating topology GeologicMapTopology...')
        arcpy.CreateTopology_management('GeologicMap','GeologicMapTopology')


	# create feature dataset StationData #
	hasStationData = False
        for fc in ['OrientationDataPoints','StationPoints','SamplePoints']:
            if fc in OptionalElements:
                hasStationData = True
                break
        addMsgAndPrint('  continue...')
	if hasStationData:
            addMsgAndPrint('  Creating feature dataset StationData...')
            try:
                    arcpy.CreateFeatureDataset_management(thisDB,'StationData')
            except:
                    addMsgAndPrint(arcpy.GetMessages(2))
            if coordSystem <> '#':
                    try:
                        arcpy.DefineProjection_management(thisDB+'/StationData',coordSystem)
                    except:
                        addMsgAndPrint(arcpy.GetMessages(2))
                        
            # create feature classes in StationData  
            # point feature classes
            featureClasses = []
            for fc in ['OrientationDataPoints','StationPoints','SamplePoints']:
                if fc in OptionalElements:
                    featureClasses.append(fc)
            for featureClass in featureClasses:	
                fieldDefs = tableDict[featureClass]
                createFeatureClass(thisDB,'StationData',featureClass,'POINT',fieldDefs)
            

	# create feature classes outside of GeologicMap and StationData
	# polygon feature classes
        fieldDefs = tableDict['DataSourcePolys']
        createFeatureClass(thisDB,'', 'DataSourcePolys','POLYGON',fieldDefs)
	
        # polyline feature classes
        if 'CartographicLines' in OptionalElements:
            fieldDefs = tableDict['CartographicLines']
            createFeatureClass(thisDB,'','CartographicLines','POLYLINE',fieldDefs)	
	
	# create tables #
	tables = ['DescriptionOfMapUnits','DataSources','Glossary','SysInfo']
	for tb in ['StandardLithology','ExtendedAttributes','GeologicEvents']:
            if tb in OptionalElements:
                tables.append(tb)
	for table in tables:
            addMsgAndPrint('  Creating table '+table+'...')
            try:
                arcpy.CreateTable_management(thisDB,table)
                fieldDefs = tableDict[table]
                for fDef in fieldDefs:
                    try:
                        if fDef[1] == 'String':
                            arcpy.AddField_management(thisDB+'/'+table,fDef[0],transDict[fDef[1]],'#','#',fDef[3],'#',transDict[fDef[2]])
                        else:
                            arcpy.AddField_management(thisDB+'/'+table,fDef[0],transDict[fDef[1]],'#','#','#','#',transDict[fDef[2]])
                    except:
                        addMsgAndPrint('Failed to add field '+fDef[0]+' to table '+table)
                        addMsgAndPrint(arcpy.GetMessages(2))		    
            except:
                addMsgAndPrint(arcpy.GetMessages())

        # create relationships
        # create relationship StationSampleLink
        if arcpy.Exists('StationData/StationPoints') and arcpy.Exists('StationData/SamplePoints'):
            addMsgAndPrint('  Creating relationship StationSampleLink...')
            arcpy.CreateRelationshipClass_management('StationData/StationPoints', 'StationData/SamplePoints', 'StationData/StationSampleLink', "SIMPLE", "Sample",
                "Station", "NONE", "ONE_TO_MANY", "NONE", "StationPoints_ID", "StationID")
                       

def createDatabase(outputDir,thisDB):
    addMsgAndPrint('  Creating geodatabase '+thisDB+'...')		
    try:
        if thisDB[-4:] == '.mdb':
            arcpy.CreatePersonalGDB_management(outputDir,thisDB)
        if thisDB[-4:] == '.gdb':
            arcpy.CreateFileGDB_management(outputDir,thisDB)
        return True
    except:
        addMsgAndPrint('Failed to create geodatabase '+outputDir+'/'+thisDB)
        addMsgAndPrint(arcpy.GetMessages(2))
        return False

#########################################
    
addMsgAndPrint(versionString)

if len(sys.argv) >= 6:
    addMsgAndPrint('Starting script')

    try:
        outputDir = sys.argv[1]
        if outputDir == '#':
            outputDir = os.getcwd()
        outputDir = outputDir.replace('\\','/')

        thisDB = sys.argv[2]
        # test for extension; if not given, default to file geodatabase
        if not thisDB[-4:].lower() in ('.gdb','.mdb'):
            thisDB = thisDB+'.gdb'

        coordSystem = sys.argv[3]

        if sys.argv[4] == '#':
            OptionalElements = []
        else:
            OptionalElements = sys.argv[4].split(';')
        
        nCrossSections = int(sys.argv[5])

        try:
            if sys.argv[6] == 'true':
                cartoReps = True
            else:
                cartoReps = False
        except:
            cartoReps = False
            
        # create personal gdb in output directory and run main routine
        if createDatabase(outputDir,thisDB):
            thisDB = outputDir+'/'+thisDB
            arcpy.RefreshCatalog(thisDB)
            main(thisDB,coordSystem,nCrossSections)
    
        # try to write a readme within the .gdb
        if thisDB[-4:] == '.gdb':
            try:
                arcpy.env.workspace = ''
                versionFile = open(thisDB+'/00readme.txt','w')
                versionFile.write('Geodatabase created by '+versionString+'\n')
                versionFile.close()
            except:
                addMsgAndPrint('Failed to write '+thisDB+'/00readme.txt')

    except:
	addMsgAndPrint('Failed.')
else:
    addMsgAndPrint(usage)
