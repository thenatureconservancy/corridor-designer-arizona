#########################################################################################
## Script name:     patchConfigGeneral.py
## Command line:    patchConfiguration
## ArcGIS Version:  9.1
## Last modified:   11 April 2006
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Creates patch configuration map
##                   
## Parameter List:
##                  Argv[1] Workspace
##                  Argv[2] Species name
##                  Argv[3] Habitat suitability map
##                  Argv[4] Moving window size
##                  Argv[5] Habitat quality threshold
##                  Argv[6] Minimum breeding patch size
##                  Argv[7] Minimum population patch size
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

# FUNCTIONS ------------------------------------------------------------------------------- 
def averageHsm():
    try:
        hsmAvg = workspace + '/' +'_hsa'                         
        gp.FocalStatistics_sa(hsm, hsmAvg, movingWindowSize, "MEAN", "DATA")
        return hsmAvg
    except:
        addErrorMessages(gp)        
 #----------------------------------------------------------------------------------------    
def groupPatches ():                                                                                        
    def calcPatchPixels (patchSize):    # If meters projection..could do conditional for ft projection?
        pixelHeight = desc(hsm).MeanCellHeight
        pixelWidth = desc(hsm).MeanCellWidth
        floatNumPixels = float(patchSize)*(10000/(pixelHeight*pixelWidth))
        roundedNumPixels = round(floatNumPixels)
        return roundedNumPixels    
    def groupIntoPatches(hsmAvg):   
        reclassClause = 'value >= ' + patchThresholdString  
        suitHabitat = workspace + '/' + '_sh'
        reclassRange = '0 999999 1'   
        suitHabitatReclass = workspace + '/' +'_shr'
        suitPatches = workspace + '/' + '_shp'       
        gp.ExtractByAttributes_sa(hsmAvg, reclassClause, suitHabitat)                       
        gp.Reclassify_sa(suitHabitat, 'Value', reclassRange, suitHabitatReclass, 'NODATA')  
        gp.RegionGroup_sa(suitHabitatReclass, suitPatches, 'EIGHT', 'WITHIN', 'ADD_LINK', '')
        gp.delete(suitHabitat)
        gp.delete(suitHabitatReclass)
        return suitPatches   
    def sortIntoPatchClasses(patchPixels, corePixels, suitPatches):
        reclassRange = '0 ' + str(patchPixels-1) + ' 1; ' + str(patchPixels) + ' ' + str(corePixels-1) + ' 2; ' + str(corePixels) + ' 999999999 3;'
        allReclass = workspace + '/' + 'RCLS'

        gp.Reclassify_sa(suitPatches, 'Count', reclassRange, allReclass, 'DATA')
        gp.RasterToPolygon_conversion(allReclass, outputShapefile, 'NO_SIMPLIFY', 'Value')
        gp.delete (allReclass)    #not sure if this is neccessary yet
        return outputShapefile
    
    # Call subfunctions
    try:
        gp.AddMessage('            -calculating number of pixels in a breeding patch ')
        patchPixels = calcPatchPixels(patchInt)
        gp.AddMessage('            -calculating number of pixels in a population patch ')
        corePixels = calcPatchPixels(coreInt)
        gp.AddMessage('            -grouping habitat suitability model into habitat patches ')
        suitPatches = groupIntoPatches(hsmAvg)
        gp.AddMessage('            -sorting habitat patches into different size classes ')
        patchShapefile = sortIntoPatchClasses(patchPixels, corePixels, suitPatches)
        gp.delete(suitPatches)
        return patchShapefile
    except:
        addErrorMessages(gp)        
                                                                               
# CALL FUNCTIONS -------------------------------------------------------------------------------  
try:
    # Script arguments ------------------------------#####
    hsm = sys.argv[1]    
    outputShapefile = sys.argv[2]
    movingWindowSize = sys.argv[3]
    patchThreshold = sys.argv[4]
    patchInt = sys.argv[5]
    coreInt = sys.argv[6]
    totalSteps = '2'

    toolName = 'PatchConfiguration'
    inParameters = "%s %s '%s' %s %s %s" % (hsm,
                                          outputShapefile,
                                          movingWindowSize,
                                          patchThreshold,
                                          patchInt,
                                          coreInt)    

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    userWorkspace = os.path.dirname(outputShapefile)
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    patchThresholdString = str(patchThreshold)
    logFile = createLogFile(workspace, toolName, inParameters)

    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: PatchConfiguration') 
    gp.AddMessage('')
    
    gp.AddMessage(' Step 1/'+totalSteps+') Averaging habitat suitability model')
    hsmAvg = averageHsm()
    gp.AddMessage(' Step 2/'+totalSteps+') Grouping habitat model into patches')
    groupPatches ()
    gp.delete(hsmAvg)
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp

except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp



