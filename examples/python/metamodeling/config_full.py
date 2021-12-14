# Define test case
metamodel = 'spawnrefsmalloffice' #folder containing the test case
url = 'http://127.0.0.1:80' #ACTB url, this default should work in all cases

# Define the model sensors. Do not include outputs that you wish to predict with the metamodel.
# Look at the readme file in the test case docs folder for sensor tags.
sensors = ['senHeaPow_y',
           'senHeaPow1_y',
           'senHeaPow2_y',
           'senHeaPow3_y',
           'senHeaPow4_y',
           'senCCPow_y',
           'senCCPow1_y',
           'senCCPow2_y',
           'senCCPow3_y',
           'senCCPow4_y']

# Define the outputs that you wish to identify using the metamodeling approach.
outputs = ['senTemRoom_y',
           'senTemRoom1_y',
           'senTemRoom2_y',
           'senTemRoom3_y',
           'senTemRoom4_y']

# Define the inputs that you will use to identify the model. The program will override these controls in the model to
# identify the model dynamics. You need to define the type (float or bool) and the range for floats.
inputs = {'PSZACcontroller_oveHeaCor_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveHeaPer1_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveHeaPer2_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveHeaPer3_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveHeaPer4_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveCooCor_u' : {'type' : 'bool'},
          'PSZACcontroller_oveCooPer1_u' : {'type' : 'bool'}
          'PSZACcontroller_oveCooPer2_u' : {'type' : 'bool'}
          'PSZACcontroller_oveCooPer3_u' : {'type' : 'bool'}
          'PSZACcontroller_oveCooPer4_u' : {'type' : 'bool'}
          'PSZACcontroller_oveDamCor_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveDamP1_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveDamP2_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveDamP3_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          'PSZACcontroller_oveDamP4_u' : {'type' : 'float', 'min' : 0, 'max' : 1}}

# Finally, add the exogenous variables available through forecasts, such as weather data or occupancy.
forecasts = ['TDryBul',
             'relHum',
             'HGloHor',
             'winSpe',
             'winDir',
             'InternalGainsRad[1]',
             'InternalGainsCon[1]',
             'InternalGainsLat[1]',
             'Occupancy[1]',
             'InternalGainsRad[2]',
             'InternalGainsCon[2]',
             'InternalGainsLat[2]',
             'Occupancy[2]',
             'InternalGainsRad[3]',
             'InternalGainsCon[3]',
             'InternalGainsLat[3]',
             'Occupancy[3]',
             'InternalGainsRad[4]',
             'InternalGainsCon[4]',
             'InternalGainsLat[4]',
             'Occupancy[4]',
             ]