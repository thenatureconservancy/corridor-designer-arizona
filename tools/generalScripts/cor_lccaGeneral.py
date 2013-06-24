#########################################################################################
## Script name:     cor_lccaGeneral.py
## Command line:    corridorModel
## ArcGIS Version:  9.1
## Last modified:   19 April 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Runs least-cost corridor analysis
##                   
## Parameter List:
##                  Argv[1]    Output Workspace
##                  Argv[2]    Species Name
##                  Argv[3]    Cost Raster
##                  Argv[4]    Large habitat protected block 1: ending point for LCCA
##                  Argv[5]    Large habitat protected block 2: starting point for LCCA
##                  Argv[6]    Patch configuration text file
##                  Argv[7]    Moving window
##                  Argv[8]    Patch quality threshold
##                  Argv[9]    Minimum home range patch size
##                  Argv[10]   Minimum population patch size
##
#########################################################################################
import sys, string, os, time
from gen_checkArcGisVersion import *
from gen_reportErrors import *
from gen_logFile import *
gp = checkArcGIS()
import gen_checkExtensions


# FUNCTIONS -----------------------------------------------------------------------------
def averageHsm(hsm):
    hsmAvg = workspace + '/' + specName + '_hsa'
    try:
        gp.FocalStatistics_sa(hsm, hsmAvg, movingWindowSize, "MEAN", "DATA") # For 9.1, 9.2
    except:
        print ('oh no!') # If using GUI, then correct format should automatically be added for
        # 9.0 or 9.1/2 If using command line, this could cause problems.
        #gp.FocalStatistics_sa(hsm, hsmAvg, movingWindowSize90, "MEAN", "DATA") # For 9.1, 9.2        
    gp.AddMessage ('            -averaged habitat suitability model')
    return hsmAvg
#----------------------------------------------------------------------------------------
def calcPatchReclassRange (patchInt, coreInt):
    try:
        def calcPatchPixels (patchSize):                   
            pixelHeight = desc(hsm).MeanCellHeight
            pixelWidth = desc(hsm).MeanCellWidth
            floatNumPixels = float(patchSize)*(10000/(pixelHeight*pixelWidth))
            roundedNumPixels = round(floatNumPixels)
            return roundedNumPixels   
        patchPixels = calcPatchPixels(patchInt)
        print ('number of patchPixels is: ' + str(patchPixels))
        gp.AddMessage ('            -number of patchPixels is: ' + str(patchPixels))    
        corePixels = calcPatchPixels(coreInt)
        if coreInt =='9999999':       
            print ('no cores defined')        
        else:
            gp.AddMessage ('            -number of corePixels is: ' + str(corePixels))
        patchCoreReclassRange = ('0 ' + str(patchPixels-1) + ' 1; ' + str(patchPixels) +
                        ' ' + str(corePixels-1) + ' 2; ' + str(corePixels) +
                        ' 999999999 3;')
        #Test to make sure this range is OK, number is so huge, could make stuff fail?
        return patchCoreReclassRange
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------
def findPatches (hsmPatch, wildlandBlock, patchThreshold, 
                 patchCoreReclassRange, blockPatches, outputStartingPatches): 
    def groupIntoPatches (clippedHsm, patchThreshold, wildlandBlock):   
        patchThresholdReclassClause = 'value >= ' + patchThreshold                                 
        suitHabitat = workspace + '/' + specName+'_sh'
        reclassRange = '0 99999 1'
        suitHabitatReclass = workspace + '/' + specName+'_shr'
        suitPatches = workspace + '/' + specName+'_shp'
        gp.ExtractByAttributes_sa(clippedHsm, patchThresholdReclassClause, suitHabitat)
        # WRAP THIS IN A TRY EXCEPT STATEMENT - IF THERE'S NO SUITABLE HABITAT,
        # QUIT AND REPORT ERROR TO USER
        gp.Reclassify_sa(suitHabitat, 'Value', reclassRange, suitHabitatReclass, 'NODATA')  
        gp.RegionGroup_sa(suitHabitatReclass, suitPatches, 'EIGHT', 'WITHIN', 'ADD_LINK', '')
        gp.delete(suitHabitat)
        gp.delete(suitHabitatReclass)
        gp.delete(clippedHsm)
        gp.AddMessage ('            -grouped '+ wildlandBlock + ' into suitable habitat')
        return suitPatches   
    def sortIntoPatchClasses(suitPatches, blockPatches, patchCoreReclassRange):
        allReclass = workspace + '/' + specName+'RCLS'
        gp.Reclassify_sa(suitPatches, 'Count', patchCoreReclassRange, allReclass, 'DATA')
        gp.RasterToPolygon_conversion(allReclass, blockPatches, 'NO_SIMPLIFY', 'Value')
        gp.delete(allReclass)
        try:
            gp.delete(suitPatches)
        except:
            gp.AddMessage ('            -could not delete suitPatches')
        gp.AddMessage('            -sorted into habitat patches and cores')
        return blockPatches    
    def queryPatches(blockPatches, outputStartingPatches, patchShapefile):
        lccaStart = outputStartingPatches + '3.shp'
        gp.select_analysis(patchShapefile, lccaStart, '"GRIDCODE" = 3')
        corecountstart = gp.GetCount_management(lccaStart)
        if corecountstart < 1:
            gp.delete(lccaStart)
            lccaStart = outputStartingPatches + '2.shp'
            gp.select_analysis(patchShapefile, lccaStart, '"GRIDCODE" = 2')
            corecountstart = gp.GetCount_management(lccaStart)
            if corecountstart < 1:
                gp.delete(lccaStart)
                lccaStart = outputStartingPatches + '1.shp'
                gp.select_analysis(patchShapefile, lccaStart, '"GRIDCODE" = 1')
                corecountstart = gp.GetCount_management(lccaStart)
                if corecountstart < 1:
                    gp.AddMessage("            -there is NO suitable habitat in wildland block -"+
                                  " set habitat quality threshold lower and try again") 
                else:                    
                    gp.AddMessage("            -no patches or cores in wildland block,"+
                              " selecting any available habitat instead")                
                    return lccaStart
            else:
                gp.AddMessage("            -no cores in wildland block,"+
                              "selecting patches instead")                
                return lccaStart
        else:
            #Need better message reporting - Report cores exist/don't exist
            # in starting block and ending block (could put protected block
            # path in message as variable)
            print("Cores exist in starting block")    
            gp.AddMessage('            -cores exist in wildland block')
            return lccaStart

    # Call Sub-Functions -----------------------------
    # first clip hsm
    try:
        clippedHsm = workspace + '/' + specName + '_bc'
        gp.ExtractByMask_sa(hsmPatch, wildlandBlock, clippedHsm)
        suitPatches = groupIntoPatches(clippedHsm, patchThreshold, wildlandBlock)
        patchShapefile = sortIntoPatchClasses(suitPatches, blockPatches, patchCoreReclassRange)
        outputStartingPatches = queryPatches(blockPatches, outputStartingPatches, patchShapefile)
        return outputStartingPatches
    except:
        addErrorMessages(gp)        

#----------------------------------------------------------------------------------------
def corridorAnalysis(hsm, specName, block1StartPolygon, block2StartPolygon):
    costDistance1 = workspace + '/' + specName + '_cd1'
    costDistance2 = workspace + '/' + specName + '_cd2'    
    backlinkRaster1 = workspace + '/' + specName + '_bl1'
    backlinkRaster2 = workspace + '/' + specName + '_bl2'
    outputCorridorGrid = workspace + '/' + specName + '_cst'
    print ' - Declared variables'
    
    def convertHsmToCost(hsm, specName):
        costRaster1 = workspace + "/" + specName + "_rst"
        gp.Minus_sa('100', hsm, costRaster1)
        try:
            costRaster2 = workspace + '/' + specName + '_rs2'
            gp.Con_sa(costRaster1, "1", costRaster2, costRaster1, "Value = 0")
            gp.delete (costRaster1)
            return costRaster2
        except:
            return costRaster1

    gp.AddMessage('            -converting habitat suitability model to cost')
    costRaster = convertHsmToCost(hsm, specName)
    gp.AddMessage('            -calculating cost distance raster 1')
    gp.CostDistance_sa(block1StartPolygon, costRaster, costDistance1, "", backlinkRaster1)

    gp.AddMessage('            -calculating cost distance raster 2')
    gp.CostDistance_sa(block2StartPolygon, costRaster, costDistance2, "", backlinkRaster2)

    gp.AddMessage('            -combining cost distance rasters into accumulative cost grid')
    gp.Corridor_sa(costDistance1, costDistance2, outputCorridorGrid)

    gp.AddMessage('            -deleting temp layers')
    #Allow user to keep cost distance grids - see delete temp layers from hab suit script

    gp.delete (costRaster)    
    gp.delete (costDistance1)   
    gp.delete (costDistance2)
    gp.delete (backlinkRaster1)
    gp.delete (backlinkRaster2)
    gp.AddMessage('            -building pyramids for accumulative cost grid')
    gp.BuildPyramids(outputCorridorGrid)
    return outputCorridorGrid

#----------------------------------------------------------------------------------------
def sliceCorridor(corridorGrid):
    slicesGrid = workspace + '/cor_slices'
    gp.Slice_sa(corridorGrid, slicesGrid, "1000", "EQUAL_AREA", "1")
      
    extractCor = workspace + '/slice1'
    gp.AddMessage('            -Creating the 0.1% slice')
    gp.ExtractByAttributes_sa(slicesGrid, "Value <= 1", extractCor)
    corridorShapefile = workspace + '/' + specName + '_0_1_percent_corridor'
    gp.RasterToPolygon_conversion(extractCor, corridorShapefile, "NO_SIMPLIFY", "")
    gp.delete(extractCor)
      
    sliceRange = range(1, 11, 1)
    for x in sliceRange:
        y = str(x)+'0'
        extractCor = workspace + '/slice' + str(y)                       
        reclassCor = workspace + '/' + specName + str(y) + 'r'            
        corridorShapefile = workspace + '/' + specName + '_'+ str(x) + '_0_percent_corridor'
        gp.AddMessage('            -Creating the '+str(x)+ '.0% slice')
        gp.ExtractByAttributes_sa(slicesGrid, "Value <=" + str(y), extractCor)
        gp.Reclassify_sa(extractCor, "VALUE", "0 " +str(y)+ " 1", reclassCor, "DATA")
        gp.RasterToPolygon_conversion(reclassCor, corridorShapefile, "NO_SIMPLIFY", "")
        gp.delete(extractCor)
        gp.delete(reclassCor)
        print ('Created the '+str(x)+ ' slice')
    gp.delete(slicesGrid)

    
# CALL FUNCTIONS -------------------------------------------------------------------------------  
# First check to make sure Core size is greater than Patch size
#Could wrap this in a try statement, if text file fails, then do simple lcca
try:
    # Script arguments ------------------------------#####         
##    userWorkspace = sys.argv[1]
##    specName = sys.argv[2]
##    hsm = sys.argv[3]
##    wildlandBlock1 = sys.argv[4]
##    wildlandBlock2 = sys.argv[5]
##    patchConfigTextFile = sys.argv[6]
##    movingWindowSize = sys.argv[7]
##    patchThreshold = sys.argv[8]
##    patchInt = sys.argv[9]
##    coreInt = sys.argv[10]
##    
##    toolName = 'corridorModel'
##    inParameters = '%s %s %s %s %s %s %s %s %s %s' % (userWorkspace,
##                                                      specName,
##                                                      hsm,
##                                                      wildlandBlock1,
##                                                      wildlandBlock2,
##                                                      patchConfigTextFile,
##                                                      movingWindowSize,
##                                                      patchThreshold,
##                                                      patchInt,
##                                                      coreInt
##                                                      )
    hsm = sys.argv[1]
    wildlandBlock1 = sys.argv[2]
    wildlandBlock2 = sys.argv[3]
    userWorkspace = sys.argv[4]     
    specName = sys.argv[5]  
    movingWindowSize = sys.argv[6]
    patchThreshold = sys.argv[7]
    patchInt = sys.argv[8]
    coreInt = sys.argv[9]
    
    toolName = 'CorridorModel'
    inParameters = "%s %s %s %s %s '%s' %s %s %s" % (hsm,
                                                     wildlandBlock1,
                                                     wildlandBlock2,
                                                     userWorkspace,
                                                     specName,
                                                     movingWindowSize,
                                                     patchThreshold,
                                                     patchInt,
                                                     coreInt
                                                     )  

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1 
##    userWorkspace = os.path.dirname(hsm)
    desc = gp.Describe
    gp.Extent = desc(hsm).Extent
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    totalSteps = '5'
    logFile = createLogFile(workspace, toolName, inParameters)
    
    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: CorridorModel') 
    gp.AddMessage('')

##    if os.path.exists(patchConfigTextFile):     
##        # R E A D   T A B L E
##        gp.AddMessage(' Step 1/'+totalSteps+') Calculating patch sizes using patch config text file')
##        myFile = open(patchConfigTextFile, 'r')
##        movingWindowSize = myFile.readline()[:-1] #need to strip off line break \n
##        patchThreshold = myFile.readline()[:-1]
##        patchInt = myFile.readline()[:-1]
##        coreInt = myFile.readline()[:-1]
##        # should do error checking for core - make sure either 0 is in
##        # file - instruct user to put 0 if no cores
##        
##        if movingWindowSize == 'Rectangle 1 1 CELL': 
##            hsmPatch = hsm
##            gp.AddMessage ('            -no neighborhood defined for averaging habitat suitability model')
##        elif movingWindowSize == 'Rectangle, 1, 1,CELL':  #For ArcGIS 9.0
##            gp.AddMessage ('            -no neighborhood defined for averaging habitat suitability model')   
##        else:
##            hsmPatch = averageHsm(hsm)
##            gp.AddMessage ('            -averaged habitat suitability model using '+ str(movingWindowSize)+ ' neighborhood')
        
    if movingWindowSize == 'Rectangle 1 1 CELL':
        print ('no moving window defined')
    elif movingWindowSize == 'Rectangle, 1, 1,CELL':  #For ArcGIS 9.0
        print ('no moving window defined')        
    else:
        gp.AddMessage(' Step 1/'+totalSteps+') Calculating patch sizes using user parameters')
        hsmPatch = averageHsm(hsm)
        gp.AddMessage ('            -averaged habitat suitability model using '+ str(movingWindowSize)+ ' neighborhood')
        
    # -------------------------------------------------------------------    
    # If patches and cores aren't defined, then use hsm and run
    # corridor analysis with user-input wildland blocks
    if patchInt == '0': #OK
        totalSteps = '2'
        gp.AddMessage(' Step 1/'+totalSteps+') No patches defined...creating corridor model using Wildland Blocks as start/end points...this may take awhile')       
        outputCorridor = corridorAnalysis(hsm, specName, wildlandBlock1, wildlandBlock2) #OK
        gp.AddMessage(' Step 2/'+totalSteps+') Slicing up corridor model into different widths')
        sliceCorridor(outputCorridor)
        gp.AddMessage(' Finished! ')
        gp.AddMessage('  ')
        closeLogFile(logFile)

    # If patches and cores defined, then figure out starting points within wildland blocks
    else:
        block1Patches = workspace + '/'+ specName + '_block1patches.shp'
        block2Patches = workspace + '/'+ specName + '_block2patches.shp'
        outputStartingPatches1 = workspace + '/'+ specName + '_block1start'     
        outputStartingPatches2 = workspace + '/'+ specName + '_block2start'

        # if user doesn't supply cores, only patches, then give core a really
        # huge number to make sure there are none in output starting blocks.   
        if coreInt == '0':
            coreInt = '9999999'
            # calculate number of pixels needed for patch and core sizes
            gp.AddMessage(' Step 2/'+totalSteps+') No cores defined - finding starting patches within Wildland Block 1')
            patchCoreReclassRange = calcPatchReclassRange(patchInt, coreInt)
            # find starting patches w/in each wildland block
            block1StartPolygon = findPatches(hsmPatch, wildlandBlock1,
                                             patchThreshold, patchCoreReclassRange,
                                             block1Patches, outputStartingPatches1)
            gp.AddMessage(' Step 3/'+totalSteps+') No cores defined - finding starting patches within Wildland Block 2')
            block2StartPolygon = findPatches(hsmPatch, wildlandBlock2,
                                             patchThreshold, patchCoreReclassRange,
                                             block2Patches, outputStartingPatches2)
            # BEFORE LCCA, NEED TO INVERSE HSM!!!!!!!!!!!!!!!!!!!
            # run corridor analysis
            gp.AddMessage(' Step 4/'+totalSteps+') Creating corridor model...this may take awhile')
            outputCorridor = corridorAnalysis(hsm, specName,
                                              block1StartPolygon, block2StartPolygon)
            gp.AddMessage(' Step 5/'+totalSteps+') Slicing up corridor model into different widths')
            sliceCorridor(outputCorridor)
            gp.AddMessage(' Finished! ')
            gp.AddMessage('  ')
            closeLogFile(logFile)
            
        # otherwise, if user supplies both patch and core numbers, use 'em.         
        else:
            # calculate number of pixels needed for patch and core sizes
            gp.AddMessage(' Step 2/'+totalSteps+') Finding starting patches & cores within Wildland Block 1')            
            patchCoreReclassRange = calcPatchReclassRange(patchInt, coreInt)
            # find starting patches w/in each wildland block
            block1StartPolygon = findPatches(hsmPatch, wildlandBlock1,
                                             patchThreshold, patchCoreReclassRange,
                                             block1Patches, outputStartingPatches1)
            gp.AddMessage(' Step 3/'+totalSteps+') Finding starting patches & cores within Wildland Block 2')           
            block2StartPolygon = findPatches(hsmPatch, wildlandBlock2,
                                             patchThreshold, patchCoreReclassRange,
                                             block2Patches, outputStartingPatches2)
            # run corridor analysis
            # BEFORE LCCA, NEED TO INVERSE HSM!!!!!!!!!!!!!!!!!!!
            gp.AddMessage(' Step 4/'+totalSteps+') Creating corridor model...this may take awhile')            
            outputCorridor = corridorAnalysis(hsm, specName,
                                              block1StartPolygon, block2StartPolygon)
            gp.AddMessage(' Step 5/'+totalSteps+') Slicing up corridor model into different widths')
            sliceCorridor(outputCorridor)
            gp.AddMessage(' Finished! ')
            gp.AddMessage('  ')
            closeLogFile(logFile)

except:
    addErrorMessages(gp)
    closeLogFile(logFile)
del gp