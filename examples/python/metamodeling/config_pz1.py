# Define test case
metamodel = 'spawnrefsmalloffice' #folder containing the test case
url = 'http://127.0.0.1:80' #ACTB url, this default should work in all cases

# Training and testing periods
start = ('20/01/01 00:00:00') #YMD HMS
training = {'start' : 0 * 24 * 3600,
            'freefloat' : [0 * 24 * 3600, 5 * 24 * 3600],
            'rbc' : [5 * 24 * 3600, 20 * 24 * 3600],
            'randomized' : [5 * 24 * 3600, 30 * 24 * 3600]}
testing = [30 * 24 * 3600, 34 * 24 * 3600] # not used yet

# Define the proportion of free-floating to controlled time
freefloat = 0.15
var = 0.05
outpath = 'output'
filename = metamodel + '.csv'

# Fine-tune the identification process


# List the model sensors. Do not include outputs that you wish to predict with the metamodel.
# Look at the readme file in the test case docs folder for sensor tags.
sensors = ['senHeaPow1_y',]
           #'senCCPow1_y']

# List the outputs that you wish to identify using the metamodeling approach.
outputs = {'senTemRoom1_y' : {'min' : 250, 'max' : 350}}

# Define the inputs that you will use to identify the model. The program will override these controls in the model to
# identify the model dynamics. You need to define the type (float or bool) and the range for floats.
inputs = {'PSZACcontroller_oveHeaPer1_u' : {'type' : 'float', 'min' : 0, 'max' : 1},
          #'PSZACcontroller_oveCooPer1_u' : {'type' : 'bool'},
          'PSZACcontroller_oveDamP1_u' : {'type' : 'float', 'min' : 0, 'max' : 1}}

# Finally, add the exogenous variables available through forecasts, such as weather data or occupancy.
forecasts = ['TDryBul',
             'HGloHor',
             'InternalGainsRad[perimeter_zn_1]',
             'InternalGainsCon[perimeter_zn_1]',
             'InternalGainsLat[perimeter_zn_1]',
             'Occupancy[perimeter_zn_1]',
             ]