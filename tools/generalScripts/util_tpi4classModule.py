#########################################################################################
## Script name:     tpi4classModule.py
## Command line:    none - called by util_prepareWorkspaceAZ or util_tpi4classMain
## ArcGIS Version:  9.1
## Last modified:   25 January 2007
## Author:          Dan Majka (dan@corridordesign.org)
## Description:     Creates topographic position index with 4 classes - gentle slopes,
##                  steep slopes, ridgetops, and canyonbottoms
##
##                  Called by prepareWorkspaceAZ and util_tpi4classMain
#########################################################################################                                                               # Import system modules
import sys, string, os, time

#----------------------------------------------------------------------------------------
# Derive slope in degrees
def deriveSlope(gp, workspace, elevationGrid):
    slopeOutput = workspace+ 'slope_deg'
    gp.Slope_sa(elevationGrid, slopeOutput, "DEGREE")
    return slopeOutput

#----------------------------------------------------------------------------------------
# Create TPI Grid
def createTpiGrid(gp, workspace, elevationGrid, tpiNeighborhood):
    elevationNeighborhood = workspace+ 'belev_neigh'
    tpiGrid = workspace+ 'tpi'
    gp.FocalStatistics_sa(elevationGrid, elevationNeighborhood, tpiNeighborhood, "MEAN", "DATA")
    gp.Minus_sa(elevationGrid,elevationNeighborhood,tpiGrid)
    gp.delete(elevationNeighborhood)
    return tpiGrid

#----------------------------------------------------------------------------------------
# Create Slope Position Grid
def createSlopePositionGrid(gp, outputTpi, workspace, tpiGrid, slopeOutput, canyonsThreshold, ridgesThreshold, slopesThreshold, deleteTpiGrid):
    canyonsRidgesReclass =  outputTpi
    slopesRaster =          workspace+ 'tpi_slopes'
    slopesClause =          'value > '+canyonsThreshold+ ' AND value < ' +ridgesThreshold
    slopesRasterReclass =   workspace+ 'tpi_slopes_t'
    slopeTimes =            workspace+ 'tpi_slope_ti'
    slopesTPI =             workspace+ 'tpi_slope_r'

    gp.Reclassify_sa(tpiGrid, 'VALUE', '-9999 ' +canyonsThreshold+ ' 1;'+ridgesThreshold+ ' 9999 4', canyonsRidgesReclass, "DATA")
    gp.AddMessage("            -extracted canyons and ridges")

    gp.ExtractbyAttributes_sa(tpiGrid,slopesClause,slopesRaster)
    gp.Reclassify_sa(slopesRaster, 'VALUE', canyonsThreshold+ ' '+ridgesThreshold+ ' 1', slopesRasterReclass, "DATA")
    gp.AddMessage("            -extracted slopes raster")

    gp.Times_sa(slopesRasterReclass,slopeOutput,slopeTimes)
    gp.AddMessage("            -multiplied slopes tpi by slopes degree")

    gp.Con_sa(slopeTimes,'3',slopesTPI,'2','VALUE > ' +slopesThreshold)
    gp.AddMessage("            -reclassified slopes")

    gp.Mosaic_management(slopesTPI,canyonsRidgesReclass)
    gp.AddMessage("            -merged layers")

    gp.AddMessage ("            -deleting temp layers")    
    gp.delete(slopesRaster)
    gp.delete(slopesRasterReclass)
    gp.delete(slopeTimes)
    gp.delete(slopesTPI)
    if deleteTpiGrid =='true':
        gp.delete(tpiGrid)
    else:
        gp.AddMessage("            -TPI Grid is saved in working directory")       
    return canyonsRidgesReclass