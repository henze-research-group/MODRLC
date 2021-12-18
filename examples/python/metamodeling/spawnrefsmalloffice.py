import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'metamodeling'))
from metamodeling import Metamodel
import config_full as config


output = str(Path(__file__).parent.absolute() / config.outpath)
meta = Metamodel(step = 300, config=config, method='N4SID')
meta.generate_matrices(output, generatedata=False, modelselection='')