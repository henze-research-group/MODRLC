import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent))
from metamodeling import Metamodel
import config_testing as config

metamodel = Metamodel(300, config, None)

metamodel.create_id_and_folders()
metamodel.pre_process_data()
metamodel.select_method()
metamodel.write_metaparams()
