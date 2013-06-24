#########################################################################################
## Script name:     sliceCorridor.py
## Command line:    sliceCorridor
## ArcGIS Version:  9.1
## Last modified:   26 January 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Creates different 'slices' from corridor grid
##                   
## Parameter List:
##                  Argv[1]    corridorGrid
##                  Argv[2]    lower slice boundary
##                  Argv[3]    upper slice boundary
##                  Argv[4]    slice interval
##
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

#---------------------------------------------------------------------------------------
def sliceCorridor(specName, corridorGrid, lowerSlice, upperSlice, sliceInterval, workspace):
    try:
        slicesGrid = workspace + '/cor_slices'
        gp.Slice_sa(corridorGrid, slicesGrid, "1000", "EQUAL_AREA", "1")
        if sliceInterval[0:2] == '0.':
            if lowerSlice == '0' and sliceInterval=='0.1':
                lowerSlice = 1
            elif lowerSlice == '0' and sliceInterval=='0.2':
                lowerSlice = 2
            elif lowerSlice == '0' and sliceInterval=='0.5':
                lowerSlice = 5
            else:
                lowerSlice = (int(lowerSlice)*10)
            print str(lowerSlice)
            upperSlice2 = (int(upperSlice)*10)
            sliceInterval2 = (int(float(sliceInterval)*10))
            sliceRange = range(lowerSlice, upperSlice2, sliceInterval2)   
            for x in sliceRange:
                try:
                    extractCor = workspace + '/slice' + str(x)
                    reclassCor = workspace + '/' + specName + str(x) + 'r'
                    if x < 10:
                        corridorShapefile = workspace + '/' + specName + '_0_'+ (str(x)[-1]) +'_percent_corridor'
                    else:
                        corridorShapefile = workspace + '/' + specName + '_'+ (str(x)[:-1]) +'_'+ (str(x)[-1]) +'_percent_corridor'                               
                    gp.AddMessage('            -creating the '+(str(x)[:-1])+ '.'+(str(x)[-1]) + '% slice')
                    gp.ExtractByAttributes_sa(slicesGrid, "Value <=" + str(x), extractCor)
                    gp.Reclassify_sa(extractCor, "VALUE", "0 " +str(x)+ " 1", reclassCor, "DATA")
                    gp.RasterToPolygon_conversion(reclassCor, corridorShapefile, "NO_SIMPLIFY", "")
                    gp.delete(extractCor)
                    gp.delete(reclassCor)
                    print ('Created the '+str(x)+ ' slice')
                except:
                    print ('Could not create the '+str(x)+ ' slice')
                    gp.AddMessage('Could not create the '+str(x)+ ' slice')
        else:       
            sliceRange = range(int(lowerSlice), int(upperSlice), int(sliceInterval))   
            for x in sliceRange:
                try:
                    y = str(x)+'0'
                    extractCor = workspace + '/slice' + str(y)                       
                    reclassCor = workspace + '/' + specName + str(y) + 'r'           
                    corridorShapefile = workspace + '/' + specName + '_'+ str(x) + '_0_percent_corridor' 
                    gp.AddMessage('            -creating the '+str(x)+ '.0% slice')
                    gp.ExtractByAttributes_sa(slicesGrid, "Value <=" + str(y), extractCor)
                    gp.Reclassify_sa(extractCor, "VALUE", "0 " +str(y)+ " 1", reclassCor, "DATA")
                    gp.RasterToPolygon_conversion(reclassCor, corridorShapefile, "NO_SIMPLIFY", "")
                    gp.delete(extractCor)
                    gp.delete(reclassCor)
                    print ('Created the '+str(x)+ ' slice')
                except:
                    print ('Could not create the '+str(x)+ ' slice')
                    gp.AddMessage('Could not create the '+str(x)+ ' slice')
        gp.delete(slicesGrid)
    except:
        addErrorMessages(gp)        
    
# CALL FUNCTIONS -----------------------------------------------------------------------
try:
   
    # Script arguments ------------------------------#####
    corridorGrid = sys.argv[1]
    lowerSlice = sys.argv[2]
    upperSlice = sys.argv[3]
    sliceInterval = sys.argv[4]
    specName = (os.path.basename(corridorGrid))[:-4]

    toolName = 'SliceCorridor'
    inParameters = '%s %s %s %s' % (corridorGrid,
                                    lowerSlice,
                                    upperSlice,
                                    sliceInterval)    

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    userWorkspace = os.path.dirname(corridorGrid) 
    gp.Extent = desc(corridorGrid).Extent
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    gp.RefreshCatalog(workspace)
    totalSteps = '1'
    logFile = createLogFile(workspace, toolName, inParameters)

    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: sliceCorridor') 
    gp.AddMessage('')
    
    gp.AddMessage(' Step 1/'+totalSteps+') Slicing up cumulative cost layer into different corridor widths')
    sliceCorridor(specName, corridorGrid, lowerSlice, upperSlice, sliceInterval, workspace)
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    del gp
    closeLogFile(logFile)