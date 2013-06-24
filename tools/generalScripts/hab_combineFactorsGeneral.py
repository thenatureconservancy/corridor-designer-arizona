# Script name:     combineFactorsGeneral.py                          
# Command line:    none; called by hsiMain                      
# ArcGIS Version:  9.1                                          
# Last modified:   12 February 2006                             
# Author:          Dan Majka (dan@corridordesign.org)           
# Description:     Combines multiple factors using a geometric or additive mean
# ---------------------------------------------------------------
#----------------------------------------------------------------------------------------
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
    # build dictionary with factor & weight pairs
    activeFactorDict = {fact1: fact1WeightFl, fact2: fact2WeightFl, fact3: fact3WeightFl,
                        fact4: fact4WeightFl, fact5: fact5WeightFl, fact6: fact6WeightFl}
    del activeFactorDict['#']   # Since must have unique key, all null factors get lumped into '#:0' dict item.
    activeFactorDict2 = {}      # Create new blank dictionary
    for x in activeFactorDict.items():  #For all key, value pairs (.items function converts each key,value pair to tuple)
        if x[1] == '0':         # Assuming all input from ArcToolbox comes in as strings; could write this to sniff out integers or do elif: statement to look for 0 elif '0'      
           gp.AddMessage ('WARNING: factor '+ str(x) + ' has no weight!')        # If the second item (value) in the tuple is 0, quit out of program, give user warning
        else:
            activeFactorDict2[x[0]] = x[1]  # Otherwise, add tuple back to new dictionary
    return activeFactorDict2

#----------------------------------------------------------------------------------------
def geometricHsm (activeFactorDict):
    expressionList = []
    for x in activeFactorDict.keys():
        factorWeight = activeFactorDict[x]
        factorExpression = '( pow (' + x + ' , ' +factorWeight+ '))'  
        expressionList.append(factorExpression)
    hsmString = " * ".join(expressionList)          # Use '*' operator to join items in list
    gp.AddMessage ('            - creating geometric HSM model. Location is '+outputHsm)    
    gp.SingleOutputMapAlgebra_sa (hsmString, outputHsm)  
    return outputHsm

#----------------------------------------------------------------------------------------
def additiveHsm (activeFactorDict):
    expressionList = []
    for x in activeFactorDict.keys():
        factorWeight = activeFactorDict[x]
        factorExpression = '(' + x + ' * ' +factorWeight+ ')'    
        expressionList.append(factorExpression)
    hsmString = " + ".join(expressionList)          # Use '+' operator to join items in list
    gp.AddMessage ('            - creating additive HSM model. Location is '+outputHsm)
    gp.SingleOutputMapAlgebra_sa (hsmString, outputHsm)        
    return outputHsm

#----------------------------------------------------------------------------------------
# CALL FUNCTIONS

# Script arguments ------------------------------#####
try:
    hsmType = sys.argv[1]
    outputHsm = sys.argv[2]
    fact1 = sys.argv[3]
    fact1Weight = sys.argv[4]
    fact2 = sys.argv[5]
    fact2Weight = sys.argv[6]
    fact3 = sys.argv[7]
    fact3Weight = sys.argv[8]
    fact4 = sys.argv[9]
    fact4Weight = sys.argv[10]
    fact5 = sys.argv[11]
    fact5Weight = sys.argv[12]
    fact6 = sys.argv[13]
    fact6Weight = sys.argv[14]
    totalSteps = '2'

    toolName = 'CombineHabitatFactors'
    inParameters = "'%s' %s %s %s %s %s %s %s %s %s %s %s %s %s" % (hsmType,
                                                                  outputHsm,
                                                                  fact1,
                                                                  fact1Weight,
                                                                  fact2,
                                                                  fact2Weight,
                                                                  fact3,
                                                                  fact3Weight,
                                                                  fact4,
                                                                  fact4Weight,
                                                                  fact5,
                                                                  fact5Weight,
                                                                  fact6,
                                                                  fact6Weight)    

    # Might want to do error checking to remove any instances of the user trying to use the same raster
    # as two different habitat factors

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
    gp.AddMessage('RUNNING: CombineHabitatFactors') 
    gp.AddMessage('')

    gp.AddMessage(' Step 1/'+totalSteps+') Checking sum of factor weights')

    
    factorSum = checkFactorWeightsSum()
    if factorSum == '100':
        fact1WeightFl = str((float(fact1Weight))/100)
        fact2WeightFl = str((float(fact2Weight))/100)
        fact3WeightFl = str((float(fact3Weight))/100)
        fact4WeightFl = str((float(fact4Weight))/100)
        fact5WeightFl = str((float(fact5Weight))/100)
        fact6WeightFl = str((float(fact6Weight))/100)
        activeFactorDict = buildFactorDictionary()

        if hsmType =='Geometric Mean':
            gp.AddMessage(' Step 2/'+totalSteps+') Combining habitat factors using Geometric Mean model')
            hsm = geometricHsm(activeFactorDict)

        elif hsmType =='Additive Mean':
            gp.AddMessage(' Step 2/'+totalSteps+') Combining habitat factors using Additive Mean model')
            hsm = additiveHsm(activeFactorDict)

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