#########################################################################################
## Script name:     lccaAZ.py
## Command line:    lccaAZ
## ArcGIS Version:  9.1
## Last modified:   05 August 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Runs corridor analysis
##                   
## Parameter List:
##                  Argv[1]    Habitat Suitability Model
##                  Argv[2]    Species
##                  Argv[3]    Patches shapefile
##                  Argv[4]    Wildland protected block 1: starting point for LCCA
##                  Argv[5]    Wildland protected block 2: ending point for LCCA
##
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
def groupPatches ():
    try:
        def calcPatchPixels (patchSize):    # If meters projection..could do conditional for ft projection?
            pixelHeight = desc(hsm).MeanCellHeight
            pixelWidth = desc(hsm).MeanCellWidth
            floatNumPixels = float(patchSize)*(10000/(pixelHeight*pixelWidth))
            roundedNumPixels = round(floatNumPixels)
            return roundedNumPixels
        specDirPathString = hab_hsmUtilities.checkSpecDirPath(gp) 
        patchTable = open(specDirPathString + specName + '/' + specName + '_patches.txt')  
        movingWindowSize = patchTable.readline()[:-1] 
        patchInt = patchTable.readline()[:-1]
        coreInt = patchTable.readline()
        patchTable.close()       
        patchPixels = calcPatchPixels(patchInt)
        corePixels = calcPatchPixels(coreInt)
        reclassRange = ('0 ' + str(patchPixels-1) + ' 1; ' + str(patchPixels) +
                        ' ' + str(corePixels-1) + ' 2; ' + str(corePixels) + ' 999999999 3;')
        return reclassRange
    except:
        addErrorMessages(gp)        
#----------------------------------------------------------------------------------------
def findStartPatches(protectedBlock, outputShapefile, startPolygon):
    def findPatches(protectedBlock, outputShapefile):
        lccaPatch = workspace + '/'+ specName + '_lcca_patch.shp'  
        clipPatch = workspace + '/'+ specName + '_cp'
        suitPatchesBlocks = workspace + '/'+ specName + '_sb'
        reclassBlocks = workspace + '/'+ specName + '_rb'
        reclassBlocksShape = outputShapefile 
        
        gp.Clip_analysis(sitewidePatches, protectedBlock, lccaPatch,"")
        gp.FeatureToRaster_conversion(lccaPatch, "GRIDCODE", clipPatch, hsm)
        gp.RegionGroup_sa(clipPatch, suitPatchesBlocks, "EIGHT", "WITHIN", "ADD_LINK", "")
        gp.Reclassify_sa(suitPatchesBlocks, "Count", reclassRange, reclassBlocks, "DATA")  
        gp.RasterToPolygon_conversion(reclassBlocks, reclassBlocksShape, "NO_SIMPLIFY", "Value")      
        gp.delete(lccaPatch)
        gp.delete(clipPatch)
        gp.delete(suitPatchesBlocks)
        gp.delete(reclassBlocks)
        return reclassBlocksShape
    
    def queryPatches(reclassBlocksShape, startPolygon):
        try:
            lccaStart = startPolygon + '3.shp'  
            gp.select_analysis(reclassBlocksShape, lccaStart, '"GRIDCODE" = 3')
            corecountstart = gp.GetCount_management(lccaStart)
            if corecountstart < 1:
                gp.delete(lccaStart)
                lccaStart = startPolygon + '2.shp'
                gp.select_analysis(reclassBlocksShape, lccaStart, '"GRIDCODE" = 2')
                corecountstart = gp.GetCount_management(lccaStart)
                if corecountstart < 1:
                    gp.delete(lccaStart)
                    lccaStart = startPolygon + '1.shp'
                    gp.select_analysis(reclassBlocksShape, lccaStart, '"GRIDCODE" = 1')
                    corecountstart = gp.GetCount_management(lccaStart)
                    if corecountstart < 1:
                        gp.AddMessage("            -there is NO suitable habitat in wildland block -"+
                                      " set habitat quality threshold lower and try again") 
                    else:
                        gp.AddMessage("            -no patches or cores in wildland block, selecting any available habitat instead")                
                        return lccaStart
                else:
                    gp.AddMessage("            -no cores in wildland block, selecting patches instead")
                    return lccaStart
            else:
                gp.AddMessage("            -cores exist in wildland block") 
                return lccaStart
        except:
            addErrorMessages(gp)

    # Call Sub-Functions ----------------
    try:
        reclassBlocksShape = findPatches(protectedBlock, outputShapefile)
        startEndPolygon = queryPatches(reclassBlocksShape, startPolygon)
        return startEndPolygon
    except:
        addErrorMessages(gp)
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
def corridorAnalysis(hsm, specName, block1StartPolygon, block2StartPolygon):
    try:
        costDistance1 = workspace + '/' + specName + '_cd1'
        backlinkRaster1 = workspace + '/' + specName + '_bl1'
        costDistance2 = workspace + '/' + specName + '_cd2'
        backlinkRaster2 = workspace + '/' + specName + '_bl2'
        outputCorridorGrid = workspace + '/' + specName + '_cst'
        print ' - Declared variables'
        
        def convertHsmToCost(hsm, specName):
            inExpression = '(100 - ' +hsm+ ')'
            costRaster1 = workspace + '/' + specName + '_rst'
            gp.SingleOutputMapAlgebra_sa(inExpression, costRaster1)            
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
        gp.AddMessage('            -combining cost distance rasters into total accumulative cost grid')        
        gp.Corridor_sa(costDistance1, costDistance2, outputCorridorGrid)
        gp.AddMessage('            -deleting temp layers')
        #Allow user to keep cost distance grids - see delete temp layers from hab suit script
        gp.delete (costRaster)
##        gp.delete (costDistance1)   
##        gp.delete (costDistance2)
        gp.delete (backlinkRaster1)
        gp.delete (backlinkRaster2)
        gp.AddMessage('            -building pyramids for total accumulative cost grid')
        gp.BuildPyramids(outputCorridorGrid)
        return outputCorridorGrid
    except:
        addErrorMessages(gp)

#----------------------------------------------------------------------------------------
def sliceCorridor(corridorGrid):
    try:
        slicesGrid = workspace + '/cor_slices'
        gp.Slice_sa(corridorGrid, slicesGrid, "1000", "EQUAL_AREA", "1")
        
        # First get 0.1% slice. Can't find creative way to get this within for loop    
        extractCor = workspace + '/slice1'
        gp.AddMessage('            -creating the 0.1% slice')         
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
            gp.AddMessage('            -creating the '+str(x)+ '.0% slice')
            gp.ExtractByAttributes_sa(slicesGrid, "Value <=" + str(y), extractCor)
            gp.Reclassify_sa(extractCor, "VALUE", "0 " +str(y)+ " 1", reclassCor, "DATA")
            gp.RasterToPolygon_conversion(reclassCor, corridorShapefile, "NO_SIMPLIFY", "")
            gp.delete(extractCor)
            gp.delete(reclassCor)
            print ('Created the '+str(x)+ ' slice')

        gp.delete(slicesGrid)
    except:
        addErrorMessages(gp)
    
# CALL FUNCTIONS -------------------------------------------------------------------------------          
try:   
    # Script arguments ------------------------------#####
    hsm = sys.argv[1]
    species = sys.argv[2]    
    sitewidePatches = sys.argv[3]
    protectedBlock1 = sys.argv[4]
    protectedBlock2 = sys.argv[5]

    toolName = 'CorridorModelAZ'
    inParameters = "%s '%s' %s %s %s" % (hsm,
                                         species,
                                         sitewidePatches,
                                         protectedBlock1,
                                         protectedBlock2)

    # Utility stuff ------------------------------#####
    gen_checkExtensions.checkSpatialAnalyst(gp)                                                 
    gp.OverwriteOutput = 1 
    userWorkspace = os.path.dirname(hsm)
    desc = gp.Describe
    gp.Extent = desc(hsm).Extent
    try:
        workspace = desc(userWorkspace).CatalogPath.replace("\\","/")
    except:
        workspace = userWorkspace
    specName = speciesDictionary.specDictLookup(species)                                                 
    totalSteps = '5'
    logFile = createLogFile(workspace, toolName, inParameters)
    
    # Call functions ------------------------------#####
    gp.AddMessage('')
    gp.AddMessage('CorridorDesigner ----------------------------------------')
    gp.AddMessage('RUNNING: Corridor Analysis Arizona') 
    gp.AddMessage('')
    
    block1Patches = workspace + '/'+ specName + '_block1patches.shp'
    block1Start = workspace + '/'+ specName + '_block1start'
    block2Patches = workspace + '/'+ specName + '_block2patches.shp'
    block2Start = workspace + '/'+ specName + '_block2start'

    gp.AddMessage(' Step 1/'+totalSteps+') Calculating patch sizes')
    reclassRange = groupPatches()
    gp.AddMessage(' Step 2/'+totalSteps+') Finding starting patches within Wildland Block 1')
    block1StartPolygon = findStartPatches(protectedBlock1, block1Patches, block1Start)
    gp.AddMessage(' Step 3/'+totalSteps+') Finding starting patches within Wildland Block 2')
    block2StartPolygon = findStartPatches(protectedBlock2, block2Patches, block2Start)  
    gp.AddMessage(' Step 4/'+totalSteps+') Creating corridor model...this may take ~5-15 minutes')
    outputCorridor = corridorAnalysis(hsm, specName, block1StartPolygon, block2StartPolygon)
    gp.AddMessage(' Step 5/'+totalSteps+') Slicing up corridor model into different widths')
    sliceCorridor(outputCorridor)
    gp.AddMessage(' Finished! ')
    gp.AddMessage('  ')
    closeLogFile(logFile)
    del gp
except:
    addErrorMessages(gp)
    closeLogFile(logFile)
    del gp