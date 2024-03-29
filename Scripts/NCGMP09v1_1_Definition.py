# ncgmp09v1.1_definition_2.py
# module with definitions for NCGMP09v1.1 geodatabase schema for 
# ArcGIS geodatabases (personal or file) for geologic map data
#  
#  Ralph Haugerud, 14 October 2010 
#  Edited by Genhan Chen, October 2012
# 

defaultLength = 255
mapUnitLength = 10
IDLength = 50
memoLength = 10485760
booleanLength = 1

# attributes are in order Name DataType NullStatus suggestedLength
# _ID is missing, as it is added programatically, below
startDict = {	# Required #
				# Tables 
				'DescriptionOfMapUnits': [['MapUnit','String','NullsOK',mapUnitLength],  
                    ['Label','String','NullsOK',30],
                    ['Name','String','NullsOK',defaultLength],
					['FullName','String','NullsOK',defaultLength],
					['Age','String','NullsOK',defaultLength],
					['Description','String','NullsOK',memoLength],
					['HierarchyKey','String','NoNulls',defaultLength],                   
					['ParagraphStyle','String','NoNulls',defaultLength],
					['AreaFillRGB','String','NullsOK',defaultLength],
                    ['AreaFillPatternDescription','String','NullsOK',defaultLength],
					['DescriptionSourceID','String','NoNulls',IDLength],
                    ['GeneralLithologyTerm','String','NullsOK',defaultLength],
                    ['GeneralLithologyConfidence','String','NullsOK',defaultLength]],
				'DataSources': [['Source','String','NoNulls',defaultLength],
					['Notes','String','NullsOK',memoLength]],
				'Glossary': [['Term','String','NoNulls',defaultLength],
					['Definition','String','NoNulls',memoLength],
					['DefinitionSourceID','String','NoNulls',IDLength]],
				# Feature classes
				'ContactsAndFaults': [['Type','String','NoNulls',defaultLength],
					['IsConcealed','SmallInteger','NullsOK',booleanLength],
					['ExistenceConfidence','String','NoNulls',IDLength],
                    ['IdentityConfidence','String','NoNulls',IDLength],
                    ['LocationConfidenceMeters','Single','NoNulls',4],
					['Label','String','NullsOK',IDLength],
                    ['DataSourceID','String','NoNulls',IDLength],
					['Notes','String','NullsOK',memoLength]],
				'DataSourcePolys': [['Notes','String','NullsOK',memoLength],
					['DataSourceID','String','NoNulls',IDLength]],
				'MapUnitPolys': [['MapUnit','String','NoNulls',mapUnitLength],
					['IdentityConfidence','String','NoNulls',IDLength],
                    ['Label','String','NullsOK',IDLength],
                    ['Symbol','String','NullsOK',defaultLength],
                    ['Notes','String','NullsOK',defaultLength],
                    ['DataSourceID','String','NoNulls',IDLength]],
				'SysInfo': [['Sub', 'String', 'NullsOK', defaultLength],
					['Pred', 'String', 'NullsOK', defaultLength],
					['Obj', 'String', 'NullsOK', defaultLength]],
				# Optional #
				# Tables
				'ExtendedAttributes': [['OwnerTable','String','NoNulls',defaultLength],
					['OwnerID','String','NoNulls',IDLength],
					['Property','String','NoNulls',defaultLength],
					['PropertyValue','String','NullsOK',defaultLength],
					['ValueLinkID','String','NullsOK',IDLength],
					['Qualifier','String','NullsOK',defaultLength],
                    ['DataSourceID','String','NullsOK',IDLength],
					['Notes','String','NullsOK',memoLength]],
				'GeologicEvents': [['Event','String','NullsOK',defaultLength],
					['AgeDisplay','String','NullsOK',defaultLength],
					['AgeYoungerTerm','String','NullsOK',defaultLength],
					['AgeOlderTerm','String','NullsOK',defaultLength],
					['TimeScale','String','NullsOK',defaultLength],
					['AgeYoungerValue','Single','NullsOK',4],
					['AgeOlderValue','Single','NullsOK',4],
					['Notes','String','NullsOK',memoLength],
					['DataSourceID','String','NullsOK',IDLength]],
				'StandardLithology': [['MapUnit','String','NullsOK',mapUnitLength],
					['Lithology','String','NullsOK',defaultLength],
					['PartType','String','NullsOK',defaultLength],
					['ProportionValue','Single','NullsOK',4],
					['ProportionTerm','String','NullsOK',defaultLength],
					['ScientificConfidence','String','NullsOK',defaultLength],
					['DataSourceID','String','NullsOK',IDLength]],
				# Feature classes
				'OtherLines': [['Type','String','NoNulls',defaultLength],
					['ExistenceConfidence','String','NoNulls',IDLength],
                    ['IdentityConfidence','String','NoNulls',IDLength],
                    ['LocationConfidenceMeters','Single','NoNulls',4],
					['Label','String','NullsOK',IDLength],
                    ['DataSourceID','String','NoNulls',IDLength],
					['Notes','String','NullsOK',memoLength]],
				'CartographicLines': [['Type','String','NullsOK',defaultLength],
                    ['Symbol','String','NullsOK',defaultLength],
					['Label','String','NullsOK',defaultLength],
                    ['DataSourceID','String','NullsOK',IDLength],
					['Notes','String','NullsOK',memoLength]],
                'OverlayPolys': [['IdentityConfidence','String','NoNulls',IDLength],
                    ['Symbol','String','NullsOK',defaultLength],
                    ['Label','String','NullsOK',IDLength],
                    ['Notes','String','NullsOK',memoLength],
					['DataSourceID','String','NoNulls',IDLength],
					['MapUnit','String','NoNulls',mapUnitLength]],
				'StationPoints': [['FieldID','String','NullsOK',defaultLength],
					['Symbol','String','NullsOK',defaultLength],
					['Label','String','NullsOK',defaultLength],
					['PlotAtScale','Integer','NullsOK',4],
					['LocationConfidenceMeters','Double','NullsOK', 8],
					['LocationMethod','String','NullsOK',defaultLength],
					['Latitude','Double','NullsOK', 8],
					['Longitude','Double','NullsOK', 8],
					['DataSourceID','String','NullsOK',IDLength]],
				'SamplePoints':      [['FieldID','String','NullsOK',defaultLength],
					['StationID','String','NoNulls',IDLength],
					['Symbol','String','NullsOK',defaultLength],
					['Label','String','NullsOK',defaultLength],
					['PlotAtScale','Integer','NullsOK',4],
					['LocationConfidenceMeters','Double','NullsOK',8],
					['DataSourceID','String','NullsOK',IDLength],
					['Notes','String','NullsOK',memoLength]],
				'OrientationDataPoints':   [['Type','String','NullsOK',defaultLength],
                    ['StationID','String','NoNulls',IDLength],
					['Label','String','NullsOK',defaultLength],
					['PlotAtScale','Integer','NullsOK',4],
					['Azimuth','Double','NullsOK',8],
					['Inclination','Double','NullsOK',8],
					['IdentityConfidence','String','NullsOK',defaultLength],
					['OrientationConfidenceDegrees','Double','NullsOK',8],
					['DataSourceID','String','NullsOK',IDLength],
					['Notes','String','NullsOK',memoLength],
					['SymbolRotation','Double','NullsOK',8]] }


enumeratedValueDomainFieldList = (
    'Type','LocationMethod','PartType','ProportionTerm','TimeScale','Qualifier',
    'Property','PropertyValue','ExistenceConfidence','IdentityConfidence',
    'ScientificConfidence','ParagraphStyle','AgeUnits', 'MapUnit',
    'DataSourceID','DefinitionSourceID','LocationSourceID','AnalysisSourceID',
    'GeneralLithology','GeneralLithologyConfidence'
    )                                  
rangeDomainDict = {
    'Azimuth':['0','360','degrees (angular measure)'],
    'Inclination':['-90','90','degrees (angular measure)']
    }
unrepresentableDomainDict = {
     '_ID':'Arbitrary string. Values should be unique within this database.',
     'PlotAtScale':'Positive real number.',
     'OrientationConfidenceDegrees':'Positive real number. Negative number indicates value is unknown.',
     'LocationConfidenceMeters':'Positive real number. Negative number indicates value is unknown.',
     'Age':'Positive real number. Zero or negative value may indicate non-numeric (e.g., limiting) age.',
     'AgePlusError':'Positive real number.',
     'AgeMinusError':'Positive real number.',
     'Notes':'Unrepresentable domain. Free text.',
     'Value':'Real number.',
     'default':'Unrepresentable domain.'
     }
attribDict = {
    '_ID':'Primary key',
    'Age':'May be interpreted (preferred) age calculated from geochronological analysis, not necessarily the date calculated from a single set of measurements.',
    'AgeMinusError':'Negative (younger) age error, measured in AgeUnits. Type of error (RMSE, 1 sigma, 2 sigma, 95% confidence limit) should be stated in Notes field.',
    'AgePlusError':'Positive (older) age error, measured in AgeUnits. Type of error (RMSE, 1 sigma, 2 sigma, 95% confidence limit) should be stated in Notes field.',
    'AgeUnits':'Units for Age, AgePlusError, AgeMinusError.',
    'AlternateSampleID':'Museum #, lab #, etc.',
    'AnalysisSourceID':'Source of analysis; foreign key to table DataSources.',
    'AreaFillPatternDescription':'Text description (e.g., "random small red dashes") provided as a convenience for users who must recreate symbolization.',
    'AreaFillRGB':'{Red, Green, Blue} tuples that specify the suggested color (e.g., "255,255,255", "124,005,255") of area fill for symbolizing MapUnit. Each color value is an integer between 0 and 255, values are zero-padded to a length of 3 digits, and values are separated by commas with no space: NNN,NNN,NNN.',
    'Azimuth':'Strike or trend, measured in degrees clockwise from geographic North. Use right-hand rule (dip is to right of azimuth direction). Horizontal planar features may have any azimuth.',
    'DataSourceID':'Source of data; foreign key to table DataSources.',
    'Definition':'Plain-language definition of Term.',
    'DefinitionSourceID':'Source of definition; foreign key to DataSources.',
    'Description':'Free-format text description of map unit. Commonly structured according to one or more accepted traditions (e.g., lithology, thickness, color, weathering and outcrop characteristics, distinguishing features, genesis, age constraints) and terse.',
    'DescriptionSourceID':'Source of map-unit description; foreign key to table Datasources.',
    'ExistenceConfidence':'Confidence that feature exists.',
    'FgdcIdentifier':'Identifier for symbol from FGDC Digital Cartographic Standard for Geologic Map Symbolization.',
    'FieldSampleID':'Sample ID given at time of collection.',
    'FullName':'Name of map unit including identification of containing higher rank unit(s), e.g., "Shnabkaib Member of Moenkopi Formation".',
    'GeneralLithology':'Categorization of map unit based on lithologic and genetic character, term selected from NGMDB standard term list.',
    'GeneralLithologyConfidence':'Describes appropriateness of GeneralLithology term for describing the map unit.',
    'HierarchyKey':'String that records hierarchical structure. Has form nn-nn-nn, nnn-nnn, or similar. Numeric, left-padded with zeros, dash-delimited. Each HierarchyKey fragment of each row MUST be the same length to allow text-based sorting of the DMU entries.',
    'IdentityConfidence':'Confidence that feature is correctly identified.',
    'Inclination':'Dip or plunge, measured in degrees down from horizontal. Negative values allowed when specifying vectors (not axes) that point above the horizon, e.g., paleocurrents. Types defined as horizontal (e.g., horizontal bedding) shall have Inclination=0.',
    'IsConcealed':'Flag for contacts and faults covered by overlying map unit.',
    'Label':'Plain-text equivalent of the desired annotation for a feature: for example "14 Ma", or "^c" which (when used with the FGDC GeoAge font) results in the geologic map-unit label TRc (with TR run together to make the Triassic symbol).',
    'LocationConfidenceMeters':'Estimated half-width in meters of positional uncertainty envelope; position is relative to other features in database.',
    'LocationSourceID':'Source of location; foreign key to table DataSources.',
    'MapUnit':'Short plain-text identifier of the map unit. Foreign key to DescriptionOfMapUnits table.',
    'MaterialAnalyzed':'Earth-material which was analyzed, e.g., wood, shell, zircon, basalt, whole-rock.',
    'Name':'Name of map unit, as shown in boldface in traditional DMU, e.g., "Shnabkaib Member". Identifies unit within its hierarchical context.',
    'NewExplanation':'Explanation of usage of symbol in this map portrayal',
    'Notes':'Additional information specific to a particular feature or table entry.',
    'OldExplanation':'Explanatory text from FGDC standard for meaning of symbol',
    'OrientationConfidenceDegrees':'Estimated angular precision of combined azimuth AND inclination measurements, in degrees.',
    'ParagraphStyle':'Token that identifies formatting of paragraph(s) within traditional Description of Map Units that correspond to this table entry.',
    'PlotAtScale':'At what scale (or larger) should this observation or analysis be plotted? At smaller scales, it should not be plotted. Useful to prevent crowding of display at small scales and to display progressively more data at larger and larger scales. Value is scale denominator.',
    'Source':'Plain-text short description that identifies the data source.',
    'StationID':'Foreign key to Stations point feature class.',
    'Symbol':'Reference to a point marker, line symbol, or area-fill symbol that is used on the map graphic to denote the feature: perhaps a star for a K-Ar age locality, or a heavy black line for a fault.',
    'Term':'Plain-language word for a concept. Values must be unique within database as a whole.',
    'Type':'Classifier that specifies what kind of geologic feature is represented by a database element: that a certain line within feature class ContactsAndFaults is a contact, or thrust fault, or water boundary; or that a point in GeochronPoints represents a K-Ar date.',
    'Value':'Numeric value (e.g., elevation, concentration) associated with an isovalue (contour, isopleth) line.)'
    }
entityDict = {
    'CartographicLines':'Lines (e.g., cross-section lines) that have no real-world physical existence, such that LocationConfidenceMeters, ExistenceConfidence, and IdentityConfidence attributes are meaningless, and that are never shown as concealed beneath a covering unit.',
    'CMULines':'Lines (box boundaries, internal contacts, brackets) of the Correlation of Map Units diagram.',
    'CMUPoints':'Points (typically, representing outcrops of a map unit too small to show as polygons at map scale) of the Correlation of Map Units diagram.',
    'CMUMapUnitPolys':'Polygons (representing map units) of the Correlation of Map Units diagram.',
    'CMUText':'Text of the Correlation of Map Units diagram.',
    'ContactsAndFaults':'Contacts between map units, faults that bound map units, and associated dangling faults. Includes concealed faults and contacts, waterlines, snowfield and glacier boundaries, and map boundary.',
    'CorrelationOfMapUnits':'Feature dataset that encodes the Correlation of Map Units (CMU) diagram found on many geologic maps. Spatial reference frame is arbitrary; units may be page inches.',
    'CrossSection':'Feature dataset equivalent to a cross section.',
    'DataSourcePolys':'Polygons that delineate data sources for all parts of the map.',
    'DataSources':'Non-spatial table of sources of all spatial features, sources of some attributes of spatial features, and sources of some attributes of non-spatial table entries.',
    'DescriptionOfMapUnits':'Non-spatial table that captures content of the Description of Map Units (or equivalent List of Map Units and associated pamphlet text) included in a traditional paper geologic map.',
    'ExtendedAttributes':'Non-spatial table for linking additional attributes to any spatial feature or non-spatial table row in the database.',
    'GeochronPoints':'Point locations of samples and accompanying geochronological measurements. Type field identifies geochronological method.',
    'GeologicEvents':'Non-spatial table for closely specifying ages of geologic features. Such ages may be tied to features via entries in table ExtendedAttributes.',
    'GeologicLines':'Lines that represent dikes, coal seams, ash beds, fold hinge-surface traces, isograds, and other lines. All have these properties: (A) They do not participate in map-unit topology. (B) They correspond to features that exist within the Earth and may be concealed beneath younger, covering, material. (C) They are located with an accuracy that likely can be estimated.',
    'GeologicMap':'Feature dataset equivalent to the map graphic: it contains all the geologic content (but not the base map) within the neatline.',
    'Glossary':'Non-spatial table that, for certain fields (including all Type fields, Confidence fields, and GeneralLithology), lists the terms that populate these fields, term definitions, and sources for definitions.',
    'IsoValueLines':'Lines that represent structure contours, concentration isopleths, and other lines that share properties of: (A) Having an associated value (e.g., elevation, concentration) that is a real number. (B ) Having a definable uncertainty in their location. (C) Describing an idealized surface that need not be shown as concealed beneath covering map units.',
    'MapUnitPolys':'Polygons that record distribution of map units (including water, snowfields, glaciers, and unmapped area) on the particular map horizon. ',
    'OrientationPoints':'Point structure data (e.g., bedding attitudes, foliation attitudes, slip vectors measured at a point, etc.), one point per measurement. Multiple measurements at a single station (e.g., bedding and cleavage) should have the same StationID.',
    'OtherPolys':'Polygons that delineate underlying material, overlying material, or some additional aspect of earth materials, e.g., dike swarm, alteration zone. On a map graphic, such polygons are commonly shown by a patterned overprint.',
    'RepurposedSymbols':'Non-spatial table that identifies symbols from the FGDC Digital Cartographic Standard for Geologic Map Symbolization (FGDC-STD-013-2006) that are "repurposed" for this map.',
    'StandardLithology':'Non-spatial table for describing the lithologic constituents of geologic map units. Has 1 to many rows per map unit. May be used to extend and supplement the GeneralLithology terms and unstructured free text Description found in the DescriptionOfMapUnits table.',
    'Stations':'Point locations of field observations and (or) samples.',    
    }



#***************************************************
tableDict = {}

# build CSA feature class attribute definitions
#startDict['CSAMapUnitPolys'] = startDict['MapUnitPolys']
#startDict['CSAContactsAndFaults'] = startDict['ContactsAndFaults']
#startDict['CSAOrientationPoints'] = startDict['OrientationPoints']

# set feature_ID definitions
for table in startDict.keys():
	oldFields = startDict[table]
	newfields = []
	newfields.append([table+'_ID','String','NoNulls',IDLength])
	for field in oldFields:
		newfields.append(field)
	tableDict[table] = newfields

# build MapUnitPoints feature class attribute definitions
tableDict['MapUnitPoints'] = tableDict['MapUnitPolys']
