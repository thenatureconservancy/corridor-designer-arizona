# Script name:     hsmGeoprocessing.py                          
# Command line:    none; called by hsiMain                      
# ArcGIS Version:  9.1                                          
# Last modified:   19 December 2006                             
# Author:          Dan Majka (dan@corridordesign.org)           
# Description:     Geoprocessing routines used by hsmMain       
# ---------------------------------------------------------------
#----------------------------------------------------------------------------------------
import os, sys, time
from gen_reportErrors import *

# Read factor weights from species weights table, add non-zero weights to activeFactorDict dictionary
def readFactorWeights (specDirPathString, specName, gp):
    try:
        specTbl = specDirPathString + specName + '/' + specName + '_weights.txt'
        factorList = ['lndcvr','elev_m','topo','dstroad']
        activeFactorDict = {}                     # Create empty dictionary
        for x in factorList:                   
            field = x
            cur = gp.SearchCursor(specTbl)
            row = cur.Next()
            factorWtInt = row.GetValue(field)
            factorWtText = str(factorWtInt)
            factorFloat = float(factorWtInt)
            factorPercent2 = factorFloat/100    # Might make variable names prettier
            factorPercent = str(factorPercent2)
                                   
            if factorFloat > 0:                 # Change this back to 0 when finished testing!     
                activeFactorDict[x] = factorPercent                                    
            else:
                print ('            -factor has a weight of 0; no reclass needed')
        print activeFactorDict
        return activeFactorDict
    except:
        addErrorMessages(gp)
    
#----------------------------------------------------------------------------------------
# Reclassify every factor in activeFactorDict
def reclassFactors(specDirPathString, specName, workspace, activeFactorDict, gp):
    for x in activeFactorDict.keys():
        missingValues = "NODATA"    # move above For statement - no need to define everytime
        factorGrid = workspace + '/basemap/' + x
        specFactorTxt = specDirPathString+ '/' + specName + '/' + specName + '_' + x +'.txt'
        factorReclass = workspace + '/output/' + specName + '/' + x + '_r'
        gp.AddMessage ('            -reclassifying habitat factor '+ x)        
        gp.ReclassByASCIIFile_sa(factorGrid, specFactorTxt, factorReclass, missingValues) 

#----------------------------------------------------------------------------------------
# Build geometric expression for each factor used in HSM. Need to be tested w/ 0-100 framework
def geometricHsm (activeFactorDict, workspace, specName, gp):
    expressionList = []
    for x in activeFactorDict.keys():
        factorReclass = workspace + '/output/' + specName + '/' + x + '_r'
        factorWeight = activeFactorDict[x]
        factorExpression = '( pow (' +factorReclass+ ' , ' +factorWeight+ '))'  
        expressionList.append(factorExpression)
    hsmString = " * ".join(expressionList)          # Use '*' operator to join items in list
    specHsm = workspace + '/output/' + specName + '/' + specName + '_hsm'
    gp.SingleOutputMapAlgebra_sa (hsmString, specHsm)  
    gp.AddMessage ('            -created geometric HSM model for '+specName+ '. Location is '+specHsm)
    return specHsm

#----------------------------------------------------------------------------------------
# Build additive expression for each factor used in HSM. Need to be tested w/ 0-100 framework
def additiveHsm (activeFactorDict, workspace, specName, gp):
    expressionList = []
    for x in activeFactorDict.keys():
        factorReclass = workspace +  '/output/' + specName + '/' + x + '_r'
        factorWeight = activeFactorDict[x]
        factorExpression = '(' +factorReclass+ ' * ' +factorWeight+ ')'    
        expressionList.append(factorExpression)
    hsmString = " + ".join(expressionList)          # Use '+' operator to join items in list
    specHsm = workspace + '/output/' + specName + '/' + specName + '_hsm'
    gp.SingleOutputMapAlgebra_sa (hsmString, specHsm)        
    gp.AddMessage ('            -created additive HSM model for '+specName+ '. Location is '+specHsm)
    return specHsm
        
#----------------------------------------------------------------------------------------
# Delete temp reclassified habitat factors
def delTempFactors (activeFactorDict, workspace, specName, gp):
    for x in activeFactorDict.keys():
        factorReclass = workspace + '/output/' + specName + '/' + x + '_r'
        gp.AddMessage ('            -deleting reclassified habitat factor '+ x)         
        gp.delete (factorReclass)
   

#----------------------------------------------------------------------------------------




