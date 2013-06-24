def checkArcGIS():
    try:
        import win32com.client
        gp = win32com.client.Dispatch('esriGeoprocessing.GpDispatch.1')
        print ('ArcGIS 9.0 or 9.1 is installed')
        return gp
    except:
        try:
            import arcgisscripting
            gp = arcgisscripting.create()
            return gp
        except:
            print ('sorry, cannot find an ArcGIS module. bailing...')
            # Problem: Can't print this out to ArcGIS window if ArcGIS module can't be found!