## Determine path of ArcGIS Install from registry
import shutil
from _winreg import *

# Determine location of ArcGIS install based on registry key
reg = OpenKey(HKEY_LOCAL_MACHINE,"SOFTWARE\\ESRI\\ArcGIS")
installDir = str(QueryValueEx(reg,"InstallDir")[0])
print installDir

# Example copy 
shutil.copy('C:/GIS/CorridorDesigner/expand.xsl','C:/')