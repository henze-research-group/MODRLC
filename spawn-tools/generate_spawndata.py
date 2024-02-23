import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))
from extract_data import FromEplus
testcase = sys.argv[1]

models_dir = Path(__file__).parent.parent.resolve().joinpath('boptest-service', 'boptest', 'testcases', testcase, 'models')
resource_dir = models_dir.joinpath('Resources')
excluded_resource_dir = models_dir.joinpath('ExcludedResources')

ep = FromEplus(str(resource_dir), str(excluded_resource_dir))
ep.generateAllData()
