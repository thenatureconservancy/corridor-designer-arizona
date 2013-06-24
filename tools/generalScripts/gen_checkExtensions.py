# Script name:     gen_checkExtensions.py                          
# Command line:    none                     
# ArcGIS Version:  9.1                                          
# Last modified:   20 December 2006                             
# Author:          Dan Majka (dan@corridordesign.org)           
# Description:     Checks out spatial analyst extension      
# ---------------------------------------------------------------
def checkSpatialAnalyst(gp):
    try:                                    # Check for spatial analyst extension
        if gp.CheckExtension('Spatial') == 'Available':
            gp.CheckOutExtension('Spatial')
            print ('spatial analyst is available')
        else:
            print ('spatial analyst is not available')
            raise 'LicenseError'       
    except 'LicenseError':
        return ('ERROR: Spatial Analyst license is not installed or unavailable')
    except:
        return gp.GetMessages(2)
        