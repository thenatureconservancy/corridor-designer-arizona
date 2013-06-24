# Script name:     hsmAdvanced.py                          
# Command line:    hsmAdvanced                      
# ArcGIS Version:  9.1                                          
# Last modified:   22 July 2007                             
# Author:          Dan Majka (dan@corridordesign.org)           
# Description:     Geoprocessing routines     
# ---------------------------------------------------------------
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions

#----------------------------------------------------------------------------------------
def checkFactorWeightsSum():
    try:
        weightSum = (int(fact1Weight) + int(fact2Weight) + int(fact3Weight) +
               int(fact4Weight) + int(fact5Weight) + int(fact6Weight))
        return str(weightSum)
    except:
        addErrorMessages(gp)        

#----------------------------------------------------------------------------------------
def buildFactorDictionary():
    try:
        # build dictionary with factor & weight pairs
        activeFactorDict = {fact1: (fact1Remap, str((float(fact1Weight))/100)), fact2: (fact2Remap, str((float(fact2Weight))/100)),
                            fact3: (fact3Remap, str((float(fact3Weight))/100)), fact4: (fact4Remap, str((float(fact4Weight))/100)),
                            fact5: (fact5Remap, str((float(fact5Weight))/100)), fact6: (fact6Remap, str((float(fact6Weight))/100))}
        del activeFactorDict['#']   # Since must have unique key, all null factors get lumped into '#:0' dict item.
        activeFactorDict2 = {}      # Create new blank dictionary
        for x in activeFactorDict.items():  #For all key, value pairs (.items function converts each key,value pair to tuple)
            if x[1][1] == '0':         # Assuming all input from ArcToolbox comes in as strings; could write this to sniff out integers or do elif: statement to look for 0 elif '0'      
               print ('factor '+ str(x[0]) + ' has no weight!')
               gp.AddMessage ('WARNING: factor '+ str(x[0]) + ' has no weight!')        # If the second item (value) in the tuple is 0, quit out of program, give user warning
            else:
                activeFactorDict2[x[0]] = x[1]  # Otherwise, add tuple back to new dictionary
        return activeFactorDict2
    except:
        addErrorMessages(gp)

#----------------------------------------------------------------------------------------
# Reclassify every factor in activeFactorDict
def reclassFactors():
    try:
        missingValues = "NODATA"
        outputDict = {}    
        for x in activeFactorDict.items(): 
            factorGrid = x[0]
            factorRemapFile = x[1][0]
            factorWeight = x[1][1]
            if len(os.path.basename(factorGrid)) < 12:
                factorReclass = workspace + '/' + (os.path.basename(factorGrid)) + '_r'
            else:
                factorReclass = workspace + '/' + (os.path.basename(factorGrid))[:-2] + '_r'
            gp.AddMessage ('            - reclassifying Habitat Factor '+ str(os.path.basename(factorGrid)) +
                           ' using the reclass file ' + factorRemapFile)
            gp.ReclassByASCIIFile_sa(factorGrid, factorRemapFile, factorReclass, missingValues)

            outputDict[factorReclass] = factorWeight      
        return outputDict
    except:
        addErrorMessages(gp)        
#----------------------------------------------------------------------------------------
def geometricHsm (reclassFactorDict):
    try:
        expressionList = []
        for x in reclassFactorDict.keys():
            factorWeight = reclassFactorDict[x]
            factorExpression = '( pow(' + x + ', ' +factorWeight+ '))'
            expressionList.append(factorExpression)
        hsmString = " * ".join(expressionList)          # Use '*' operator to join items in list
        gp.AddMessage ('            - creating geometric HSM model. Location is '+outputHsm)
        gp.SingleOutputMapAlgebra_sa (hsmString, outputHsm)  

        return hsmTemp
    except:
        addErrorMessages(gp)

#----------------------------------------------------------------------------------------
def additiveHsm (reclassFactorDict):
    try:
        expressionList = []
        for x in reclassFactorDict.keys():
            factorWeight = reclassFactorDict[x]
            factorExpression = '(' + x + ' * ' +factorWeight+ ')'    
            expressionList.append(factorExpression)
        hsmString = " + ".join(expressionList)          # Use '+' operator to join items in list
        gp.AddMessage ('            - creating additive HSM model. Location is '+outputHsm)
        gp.SingleOutputMapAlgebra_sa (hsmString, outputHsm)        

        return hsmTemp
    except:
        addErrorMessages(gp)
     
#----------------------------------------------------------------------------------------
# Delete temp reclassified habitat factors
def delTempFactors (reclassFactorDict):
    try:
        for x in reclassFactorDict.keys():
            factorReclass = x
            gp.AddMessage ('            - deleting habitat factor '+ x)            
            gp.delete (factorReclass)
    
    except:
        addErrorMessages(gp)
        
#----------------------------------------------------------------------------------------
# CALL FUNCTIONS

try:
    # Script arguments ------------------------------#####
    hsmType = sys.argv[1]
    outputHsm = sys.argv[2]
    deleteTempFactors = sys.argv[3]

    fact1 = sys.argv[4]
    fact1Remap = sys.argv[5]
    fact1Weight = sys.argv[6]

    fact2 = sys.argv[7]
    fact2Remap = sys.argv[8]
    fact2Weight = sys.argv[9]

    fact3 = sys.argv[10]
    fact3Remap = sys.argv[11]
    fact3Weight = sys.argv[12]

    fact4 = sys.argv[13]
    fact4Remap = sys.argv[14]
    fact4Weight = sys.argv[15]

    fact5 = sys.argv[16]
    fact5Remap = sys.argv[17]
    fact5Weight = sys.argv[18]

    fact6 = sys.argv[19]
    fact6Remap = sys.argv[20]
    fact6Weight = sys.argv[21]

    totalSteps = '4'

    toolName = 'HabitatSuitabilityModel'
    inParameters = "'%s' %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" % (hsmType,
                                                                                       outputHsm,
                                                                                       deleteTempFactors,
                                                                                       fact1,
                                                                                       fact1Remap,
                                                                                       fact1Weight,
                                                                                       fact2,
                                                                                       fact2Remap,
                                                                                       fact2Weight,
                                                                                       fact3,
                                                                                       fact3Remap,
                                                                                       fact3Weight,
                                                                                       fact4,
                                                                                       fact4Remap,
                                                                                       fact4Weight,
                                                                                       fact5,
                                                                                       fact5Remap,
                                                                                       fact5Weight,
                                                                                       fact6,
                                                                                       fact6Remap,
                                                                                       fact6Weight)
                                                                                       

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1                                                  
    desc = gp.Describe
    userWorkspace = os.path.dirname(outputHsm)
    try:  
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    logFile = createLogFile(workspace, toolName, inParameters)

    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: HabitatSuitabilityModel') 
    gp.AddMessage('')
    
    gp.AddMessage(' Step 1/'+totalSteps+') Checking sum of factor weights') 
    factorSum = checkFactorWeightsSum() #
    if factorSum == '100':
        activeFactorDict = buildFactorDictionary()
        # Need to check FactorWeightsSum again to make sure weights after removing #'s still sums to 100
        gp.AddMessage(' Step 2/'+totalSteps+') Reclassifying habitat factors')        
        reclassFactorDict = reclassFactors()
        hsmTemp = workspace + '/hsmTemp'
        if hsmType =='Geometric Mean':
            gp.AddMessage(' Step 3/'+totalSteps+') Combining habitat factors using Geometric Mean model')
            hsm = geometricHsm(reclassFactorDict)
        else:
            gp.AddMessage(' Step 3/'+totalSteps+') Combining habitat factors using Additive Mean model')
            hsm = additiveHsm(reclassFactorDict)

        if deleteTempFactors =='true':
            gp.AddMessage(' Step 4/'+totalSteps+') Deleting intermediate layers')
            delTempFactors(reclassFactorDict)
        else:
            gp.AddMessage(' Step 4/'+totalSteps+') Intermediate layers are saved in species directory')
        gp.AddMessage(' Finished! ')
        gp.AddMessage('  ')
        closeLogFile(logFile)
        del gp
    else:
        gp.AddMessage('')
        gp.AddMessage(' WARNING: Your factor weights sum to '+factorSum +', not 100! Check your math and try again!')
        gp.AddMessage('')
        closeLogFile(logFile)
        del gp
except:
    addErrorMessages(gp)
    try:
        closeLogFile(logFile)
        del gp
    except:
        print 'cannot close logFile'

