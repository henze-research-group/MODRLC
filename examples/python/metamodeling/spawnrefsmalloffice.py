import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'metamodeling'))
from metamodeling import Metamodel
import config_pz1 as config

output = config.outpath + '/' + config.filename
meta = Metamodel(step = 300)
meta.generate_data(config)
meta.set_identification_parameters('senTemRoom1_y', training=5, testing=2, start_day=0)
meta.split_dataset(output, 'senTemRoom1_y')
A, B, C, AK, BK, K, x = meta.extract(select='bss')
