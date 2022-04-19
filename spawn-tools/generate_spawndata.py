import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))
from extract_data import FromEplus
ep = FromEplus('../testcases/SpawnResources/', sys.argv[1])
ep.generateAllData()