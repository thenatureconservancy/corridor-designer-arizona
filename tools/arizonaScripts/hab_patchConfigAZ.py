#########################################################################################
## Script name:     patchConfig.py
## Command line:    patchConfig
## ArcGIS Version:  9.1
## Last modified:   05 April 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Creates patch configuration map
##                   
## Parameter List:
##                  Argv[1] Species name
##                  Argv[2] Habitat suitability map
##                  Argv[3] Habitat quality threshold
#########################################################################################
import sys, string, os, time
sys.path.append(os.path.split(os.path.dirname(sys.argv[0]))[0] +'/generalScripts')
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions
import speciesDictionary, hab_hsmUtilities

#----------------------------------------------------------------------------------------
def averageHsm(hsm):
    try:
        hsmAvg = workspace + '/' + specName + '_hsa'                # Make better name
        gp.FocalStatistics_sa(hsm, hsmAvg, movingWindowSize, "MEAN", "DATA")                      
        return hsmAvg
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------    
def groupPatches ():
    def calcPatchPixels (patchSize):        # If meters projection..could do conditional for ft projection?
        pixelHeight = desc(hsmAvg).MeanCellHeight
        pixelWidth = desc(hsmAvg).MeanCellWidth
        floatNumPixels = float(patchSize)*(10000/(pixelHeight*pixelWidth))
        roundedNumPixels = round(floatNumPixels)
        return roundedNumPixels
    def groupIntoPatches ():   
        reclassClause = 'value >= ' + patchThresholdString                                  
        suitHabitat = workspace + '/' + specName + '_sh'
        reclassRange = '0 999999 1'   
        suitHabitatReclass = workspace + '/' + specName + '_shr'
        suitPatches = workspace + '/' + specName + '_shp'

        gp.ExtractByAttributes_sa(hsmAvg, reclassClause, suitHabitat)                       
        gp.Reclassify_sa(suitHabitat, 'Value', reclassRange, suitHabitatReclass, 'NODATA')  
        gp.RegionGroup_sa(suitHabitatReclass, suitPatches, 'EIGHT', 'WITHIN', 'ADD_LINK', '')
        gp.delete(suitHabitat)
        gp.delete(suitHabitatReclass)
        return suitPatches
    def sortIntoPatchClasses(patchPixels, corePixels, suitPatches):
        reclassRange = '0 ' + str(patchPixels-1) + ' 1; ' + str(patchPixels) + ' ' + str(corePixels-1) + ' 2; ' + str(corePixels) + ' 999999999 3;'
        allReclass = workspace + '/' + specName + 'RCLS'
        patchShapefile = workspace + '/' + specName + '_patches.shp'

        gp.Reclassify_sa(suitPatches, 'Count', reclassRange, allReclass, 'DATA')
        gp.RasterToPolygon_conversion(allReclass, patchShapefile, 'NO_SIMPLIFY', 'Value')
        # could add text field here instead of 1/2/3 stuff:
        # gp.addfield (patchShapefile, 'Patches', 'text', '32') #does this need to be gp.addfield_management ?
        # codeBlock = 
        # gp.CalculateField_management(patchShapefile, 'Patches',codeBlock) # Probably have to use a cursor instead, since 9.1 doesn't support advanced field calculations (9.2 does)
        
        gp.delete(allReclass)  
        return patchShapefile
    
    # Call subfunctions
    try:
        gp.AddMessage('            -calculating number of pixels in a patch ')
        patchPixels = calcPatchPixels(patchInt)
        gp.AddMessage('            -calculating number of pixels in a core ')
        corePixels = calcPatchPixels(coreInt)
        gp.AddMessage('            -grouping habitat suitability model into habitat patches ')
        suitPatches = groupIntoPatches()
        gp.AddMessage('            -sorting habitat patches into different size classes ')
        patchShapefile = sortIntoPatchClasses(patchPixels, corePixels, suitPatches)
        gp.delete(suitPatches)
        return patchShapefile   # Change to allReclass if grid is needed in further steps instead.
    except:
        addErrorMessages(gp)        
                                                                               
# CALL FUNCTIONS -------------------------------------------------------------------------------

try:
    # Script arguments ------------------------------#####
    
    hsm = sys.argv[1]    
    speciesFullName = sys.argv[2]
    patchThreshold = sys.argv[3]

    toolName = 'PatchConfigurationAZ'
    inParameters = "%s '%s' %s" % (hsm,
                                 speciesFullName,
                                 patchThreshold)
    
    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    userWorkspace = os.path.dirname(hsm)
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    specName = speciesDictionary.specDictLookup(speciesFullName)
    patchThresholdString = str(patchThreshold)
    totalSteps = '2'
    logFile = createLogFile(workspace, toolName, inParameters)
    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: PatchConfigurationAZ') 
    gp.AddMessage('')

    specDirPathString = hab_hsmUtilities.checkSpecDirPath(gp)

    # Set up some variables, read patch & core sizes from table        
    patchTable = open(specDirPathString + specName + '/' + specName + '_patches.txt')  
    movingWindowSize = patchTable.readline()[:-1] 
    patchInt = patchTable.readline()[:-1]
    coreInt = patchTable.readline()
    patchTable.close()

    gp.AddMessage(' Step 1/'+totalSteps+') Averaging habitat suitability model')
    hsmAvg = averageHsm(hsm)
    gp.AddMessage(' Step 2/'+totalSteps+') Grouping habitat model into patches')
    patchShapefile = groupPatches()
    print (' 2) Reclassified suitable habitat')
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp
