#########################################################################################
## Script name:     hsmMain.py
## Command line:    HSM
## ArcGIS Version:  9.1
## Last modified:   19 December 2006
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Creates Habitat suitability model based on 4 factors -
##                  vegetation, elevation, topography, and distrance from roads. 
## Parameter List:
##                  Argv[1] Workspace
##                  Argv[2] Species name
##                  Argv[3] HSI type (geometric or additive)
##                  Argv[4] Save Intermediate data layers (yes or no)
#########################################################################################
import sys, string, os, time
sys.path.append(os.path.split(os.path.dirname(sys.argv[0]))[0] +'/generalScripts')
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions                                                      
import speciesDictionary, hab_hsmUtilities, hab_hsmGeoprocessing

# CALL FUNCTIONS -------------------------------------------------------------------------------  
try:
    # Arguments ------------------------------#####    
    userWorkspace = sys.argv[1]
    speciesFullName = sys.argv[2]
    hsmType = sys.argv[3]
    deleteTempFactors = sys.argv[4]

    toolName = 'HabitatSuitabilityModelAZ'
    inParameters = "%s '%s' '%s' %s" % (userWorkspace,
                                    speciesFullName,
                                    hsmType,
                                    deleteTempFactors) 

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    specName = speciesDictionary.specDictLookup(speciesFullName)
    totalSteps = '4'
    
    
    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: HabitatSuitabilityModelAZ') 
    gp.AddMessage('')
    
    specDirPathString = hab_hsmUtilities.checkSpecDirPath(gp)
    gp.AddMessage(' Step 1/'+totalSteps+') Creating output folder for ' + speciesFullName)
    outputFolder = hab_hsmUtilities.createOutputFolder (workspace, specName, speciesFullName, gp)
    specFolder = userWorkspace+'/output/'+specName
    logFile = createLogFile(specFolder, toolName, inParameters)
    activeFactorDict = hab_hsmGeoprocessing.readFactorWeights(specDirPathString, specName, gp)
    gp.AddMessage(' Step 2/'+totalSteps+') Reclassifying habitat factors')           
    hab_hsmGeoprocessing.reclassFactors(specDirPathString, specName, workspace, activeFactorDict, gp)


    if hsmType =='Geometric Mean':
        gp.AddMessage(' Step 3/'+totalSteps+') Combining reclassified habitat factors using '
                      + hsmType + ' model for '+ speciesFullName)        
        specHsm = hab_hsmGeoprocessing.geometricHsm(activeFactorDict, workspace, specName, gp)
    else:
        gp.AddMessage(' Step 3/'+totalSteps+') Combining reclassified habitat factors using '
                      + hsmType + ' model for '+ speciesFullName)        
        specHsm = hab_hsmGeoprocessing.additiveHsm(activeFactorDict, workspace, specName, gp)

    if deleteTempFactors =='true':
        gp.AddMessage(' Step 4/'+totalSteps+') Deleting intermediate data layers for '+ speciesFullName)         
        hab_hsmGeoprocessing.delTempFactors(activeFactorDict, workspace, specName, gp)
    else:
        gp.AddMessage(' Step 4/'+totalSteps+') Reclassified factors are saved in '+ specName + ' folder')
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp



