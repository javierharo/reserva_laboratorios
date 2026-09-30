import json
from pathlib import Path
import sys

report = json.loads(Path('coverage.json').read_text(encoding='utf-8'))
files = [v for k, v in report['files'].items() if k.replace('\\', '/').startswith('app/services/')]
covered = sum(v['summary']['covered_lines'] for v in files)
total = sum(v['summary']['num_statements'] for v in files)
services = covered / total * 100 if total else 0
global_cov = report['totals']['percent_covered']
print(f'Services: {services:.2f}% (mínimo 90%); global: {global_cov:.2f}% (mínimo 70%)')
sys.exit(0 if services >= 90 and global_cov >= 70 else 1)
