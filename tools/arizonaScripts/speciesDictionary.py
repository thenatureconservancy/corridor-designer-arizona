def specDictLookup(speciesFullName):
    specDict = {

    # To add a species, place it in the following table following
    # the example set by the existing species. Columns are tab
    # delimited. Note: the colon and comma in each row are required.
    # The species abbreviation HAS to be 9 letters or less - ArcInfo
    # grids are limited to 13 total characters, and the modeling
    # output tacks on another 4 characters to the 9 letter species
    # abbreviation.
        
    # Full species name             :       Spec. abbrev.   ,
    #-------------------------      -       -------------   -
    # Add any new species below ------------------------------------
    'Antelope jackrabbit'           :       'antjkrbt'      ,
    'Arizona gray squirrel'         :       'azgrsqrl'      ,
    'Badger'                        :       'badger'        ,
    'Bighorn sheep'                 :       'bghrnshp'      ,
    'Black bear'                    :       'blackbear'     ,
    'Black-tailed jackrabbit'       :       'btjkrbt'       ,
    'Black-tailed rattlesnake'      :       'btrattle'      ,
    'Chiricahua leopard frog'       :       'chleofrog'     ,
    'Coati'                         :       'coati'         ,
    'Coues white-tailed deer'       :       'cwtdeer'       ,
    'Desert box turtle'             :       'boxturtle'     ,
    'Desert tortoise'               :       'dsrttort'      ,
    'Elk'                           :       'elk'           ,
    'Giant spotted whiptail'        :       'gspotwhip'     ,
    'Gila monster'                  :       'gilamonst'     ,
    'Jaguar'                        :       'jaguar'        ,
    'Javelina'                      :       'javelina'      ,
    'Kit fox'                       :       'kitfox'        ,
    'Lowland leopard frog'          :       'loleofrog'     ,
    'Lyre snake'                    :       'lyresnake'     ,
    'Mountain lion'                 :       'mtnlion'       ,
    'Mule deer'                     :       'muledeer'      ,
    'Mexican garter snake'          :       'mxgrtsnak'     ,
    'Porcupine'                     :       'porcupine'     ,
    'Pronghorn'                     :       'pronghorn'     ,
    'Sonoran desert toad'           :       'sdestoad'      ,
    'Sonoran whipsnake'             :       'swhipsnak'     ,
    'Tiger rattlesnake'             :       'tgrrattle'     ,
    'Tucson shovel-nosed snake'     :       'tucshov'       ,
    # Add any new species above ------------------------------------
    }

    specName = specDict[speciesFullName]
    return specName

