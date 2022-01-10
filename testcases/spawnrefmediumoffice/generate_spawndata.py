import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent / 'spawn-tools'))
from extract_data import FromEplus

ep = FromEplus('../SpawnResources/', 'spawnrefmediumoffice')
ep.generateAllData()