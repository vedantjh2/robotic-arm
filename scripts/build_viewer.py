from pathlib import Path
root=Path(__file__).resolve().parents[1]
import json
revision=json.loads((root/'viewer/model.json').read_text())['parameters']['revision']
template='anatomy_template.html' if revision=='A1' else 'template.html'
html=(root/'viewer'/template).read_text().replace('__MODEL_DATA__',(root/'viewer/model.json').read_text())
(root/'viewer/index.html').write_text(html)
print('Wrote self-contained model data in viewer/index.html (Three.js library loads from CDN).')
