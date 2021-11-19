import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'metamodeling'))

from metamodeling import Metamodel

moddata = ['Time', 'perZon1.TAir', 'HVAC1.yHeaPow', 'weaBus.TDryBul', 'weaBus.HGloHor',
           'HVAC1.volSenOA.V_flow']
epdata = ['time', 'P1_IntGaiTot', 'P1_OccN']

include = ['HVAC1.yHeaPow', 'weaBus.TDryBul', 'weaBus.HGloHor', 'HVAC1.volSenOA.V_flow', 'P1_OccN',
           'P1_IntGaiTot']

id = Metamodel('resources/data.csv', step=300)
id.set_identification_parameters('perZon1.TAir', start_day=4)
id.split_dataset('perZon1.TAir')
A, B, C, AK, BK, K, x = id.extract()

# id.extract('override', ['HVAC1.yHeaPow', 'weaBus.TDryBul', 'weaBus.HGloHor', 'HVAC1.volSenOA.V_flow', 'P1_OccN'])
