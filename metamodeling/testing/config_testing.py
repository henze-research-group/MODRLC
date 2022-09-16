# Define test case
import numpy as np
metamodel = 'spawnrefsmalloffice' #folder containing the test case
url = 'http://127.0.0.1:80' #ACTB url, this default should work in all cases

# Training and testing periods
start = ('20/01/01 00:00:00') #YMD HMS
training = {'start' : 0 * 24 * 3600,
            'length' : 15 * 24 * 3600,
            'training' : 0.9,
            'freefloat' : 0,
            'rbc' : 0.,
            'randomized' : 1.0}

# Define the proportion of free-floating to controlled time
freefloat = 0.15
var = 0.1

# Fine-tune the identification process

# Define the model sensors. Do not include outputs that you wish to predict with the metamodel.
# Look at the readme file in the test case docs folder for sensor tags.
sensors = [#'senHeaPow_y',
           # 'senHeaPow1_y',
           # 'senHeaPow2_y',
           # 'senHeaPow3_y',
           # 'senHeaPow4_y',
           # 'senCCPow_y',
           # 'senCCPow1_y',
           # 'senCCPow2_y',
           # 'senCCPow3_y',
           # 'senCCPow4_y'
           ]

# Define the outputs that you wish to identify using the metamodeling approach.
outputs = {'senTemRoom_y' : {'min' : 250, 'max' : 350},
           'senTemRoom1_y' : {'min' : 250, 'max' : 350},
           'senTemRoom2_y' : {'min' : 250, 'max' : 350},
           'senTemRoom3_y' : {'min' : 250, 'max' : 350},
           'senTemRoom4_y' : {'min' : 250, 'max' : 350},
           #'senHeaPow_y' : {'min' : 0, 'max' : 14000},
           # 'senHeaPow1_y' : {'min' : 0, 'max' : 14000},
           # 'senHeaPow2_y' : {'min' : 0, 'max' : 14000},
           # 'senHeaPow3_y' : {'min' : 0, 'max' : 14000},
           # 'senHeaPow4_y' : {'min' : 0, 'max' : 14000},
    }

# Define the inputs that you will use to identify the model. The program will override these controls in the model to
# identify the model dynamics. You need to define the type (float or bool) and the range for floats.
inputs = {   'PSZACcontroller_oveHeaCor_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
             'PSZACcontroller_oveHeaPer1_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
             'PSZACcontroller_oveHeaPer2_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
             'PSZACcontroller_oveHeaPer3_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
             'PSZACcontroller_oveHeaPer4_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
             'PSZACcontroller_oveDamCor_u' : {'type' : 'float', 'min' : 0, 'max' : 0.5},
             'PSZACcontroller_oveDamP1_u' : {'type' : 'float', 'min' : 0, 'max' : 0.5},
             'PSZACcontroller_oveDamP2_u' : {'type' : 'float', 'min' : 0, 'max' : 0.5},
             'PSZACcontroller_oveDamP3_u' : {'type' : 'float', 'min' : 0, 'max' : 0.5},
             'PSZACcontroller_oveDamP4_u' : {'type' : 'float', 'min' : 0, 'max' : 0.5},
          }

# Finally, add the exogenous variables available through forecasts, such as weather data or occupancy.
forecasts = ['TDryBul',
             # 'relHum',
             'HGloHor',
             # 'winSpe',
             # 'winDir',
             # 'InternalGainsRad[core_zn]',
             # 'InternalGainsCon[core_zn]',
             # 'InternalGainsLat[core_zn]',
             'Occupancy[core_zn]',
             #'InternalGainsRad[perimeter_zn_1]',
             #'InternalGainsCon[perimeter_zn_1]',
             #'InternalGainsLat[perimeter_zn_1]',
             'Occupancy[perimeter_zn_1]',
             # 'InternalGainsRad[perimeter_zn_2]',
             # 'InternalGainsCon[perimeter_zn_2]',
             # 'InternalGainsLat[perimeter_zn_2]',
             'Occupancy[perimeter_zn_2]',
             # 'InternalGainsRad[perimeter_zn_3]',
             # 'InternalGainsCon[perimeter_zn_3]',
             # 'InternalGainsLat[perimeter_zn_3]',
             'Occupancy[perimeter_zn_3]',
             # 'InternalGainsRad[perimeter_zn_4]',
             # 'InternalGainsCon[perimeter_zn_4]',
             # 'InternalGainsLat[perimeter_zn_4]',
             'Occupancy[perimeter_zn_4]',
             ]

deactivate = {
              'PSZACcontroller_oveCooCor_u' : {'type' : 'bool'},
              'PSZACcontroller_oveCooPer1_u' : {'type' : 'bool'},
              'PSZACcontroller_oveCooPer2_u' : {'type' : 'bool'},
              'PSZACcontroller_oveCooPer3_u' : {'type' : 'bool'},
              'PSZACcontroller_oveCooPer4_u' : {'type' : 'bool'},
              #'PSZACcontroller_oveHeaStpCor_u' : {'type' : 'float', 'min' : 273.15 + 14, 'max' : 273.15 + 27},
              #'PSZACcontroller_oveHeaStpPer1_u' : {'type' : 'float', 'min' : 273.15 + 14, 'max' : 273.15 + 27},
              #'PSZACcontroller_oveHeaStpPer2_u' : {'type' : 'float', 'min' : 273.15 + 14, 'max' : 273.15 + 27},
              #'PSZACcontroller_oveHeaStpPer3_u' : {'type' : 'float', 'min' : 273.15 + 14, 'max' : 273.15 + 27},
              #'PSZACcontroller_oveHeaStpPer4_u' : {'type' : 'float', 'min' : 273.15 + 14, 'max' : 273.15 + 27},
              #'PSZACcontroller_oveHeaCor_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
              #'PSZACcontroller_oveHeaPer2_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
              #'PSZACcontroller_oveHeaPer3_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
              #'PSZACcontroller_oveHeaPer4_u' : {'type' : 'float', 'min' : 0, 'max' : 1},


}