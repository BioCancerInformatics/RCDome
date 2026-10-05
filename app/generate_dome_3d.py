"""Generate dome_3d.html — the RCDome 3D dome (three.js), fully functional.

- 53 entity nodes on the sphere shell + network lines (gene -> top entity).
- Lower legend L1-L5 highlights that level's entities, genes, and lines.
- Click an entity -> focused view of its FULL gene constellation (hover/click).
- The background constellation defaults to the top-400 sample for legibility,
  with a toggle to switch to the full 9,265-gene constellation.
"""
import csv, json, sys
sys.stdout.reconfigure(encoding='utf-8')
csv.field_size_limit(sys.maxsize)

CSV = "data/unified_gene_rcd_matrix_V027.csv"
OUT = "www/dome_3d.html"

LEVEL_MAP = {
    "L1 Modalities": "L1", "L2 Subtypes": "L2", "L3 Triggers": "L3",
    "L4 Functional/contextual": "L4", "L5 Generic/umbrella/taxon": "L5",
}
LEVEL_NAMES = {
    "L1": "L1 modalities", "L2": "L2 subtypes", "L3": "L3 triggers",
    "L4": "L4 Functional/contextual", "L5": "L5 Generic/umbrella/taxon",
}

entity_genes = {}
gene_ent_count = {}
entity_level = {}
with open(CSV, encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f):
        g = (row.get('gene_symbol') or '').strip()
        e = (row.get('rcd_form_canonical') or '').strip()
        lvl = LEVEL_MAP.get((row.get('rcdome_level_name') or '').strip(), 'L5')
        if not g or not e:
            continue
        entity_level.setdefault(e, lvl)
        entity_genes.setdefault(e, set()).add(g)
        gene_ent_count.setdefault(g, {}).setdefault(e, 0)
        gene_ent_count[g][e] += 1

order = {'L1': 0, 'L2': 1, 'L3': 2, 'L4': 3, 'L5': 4}
entity_list = sorted(
    [{'name': e, 'level': entity_level[e], 'n': len(gs)} for e, gs in entity_genes.items()],
    key=lambda e: (order.get(e['level'], 9), -e['n'])
)
# ALL genes (9,265), ordered by coverage then symbol
gene_symbols = sorted(gene_ent_count.keys(), key=lambda g: (-len(gene_ent_count[g]), g))
genes = []
for g in gene_symbols:
    counts = gene_ent_count[g]
    top = max(counts, key=lambda e: (counts[e], e))
    genes.append({'symbol': g, 'n': len(counts), 'top': top})

gene_index = {g: i for i, g in enumerate(gene_symbols)}
# top-400 sample (default view), by coverage
sampled = sorted(range(len(genes)), key=lambda i: (-genes[i]['n'], genes[i]['symbol']))[:400]
sampled = sorted(sampled)

entity_gene_indices = {e: [gene_index[g] for g in gs] for e, gs in entity_genes.items()}
level_genes = {lvl: set() for lvl in order}
for e, idxs in entity_gene_indices.items():
    level_genes[entity_level[e]].update(idxs)
level_genes = {lvl: sorted(s) for lvl, s in level_genes.items()}
level_counts = {lvl: sum(1 for e in entity_list if e['level'] == lvl) for lvl in order}

DATA = {
    'entities': entity_list, 'genes': genes, 'sampled': sampled,
    'entity_genes': entity_gene_indices,
    'level_genes': level_genes, 'level_counts': level_counts,
}

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RCDome — 3D RCDome</title>
<script src="three.min.js"></script>
<script src="OrbitControls.js"></script>
<style>
  body { margin:0; background:#0b1020; overflow:hidden; font-family:'Segoe UI',system-ui,sans-serif; }
  #tip { position:fixed; display:none; background:#1c1917; color:#e7e5e4; padding:8px 12px; border-radius:8px; font-size:12px; pointer-events:none; z-index:10; max-width:340px; box-shadow:0 6px 18px rgba(0,0,0,.4); }
  #focus_header { position:fixed; top:16px; left:50%; transform:translateX(-50%); display:none; background:#1c1917; color:#e7e5e4; padding:10px 18px; border-radius:999px; font-size:14px; z-index:9; box-shadow:0 6px 18px rgba(0,0,0,.4); }
  #back_btn { position:fixed; top:16px; left:16px; display:none; background:#FF9800; color:#0b1020; border:none; border-radius:999px; padding:8px 16px; font-size:13px; font-weight:700; cursor:pointer; z-index:9; }
  #full_btn { position:fixed; top:16px; right:16px; background:#1d4ed8; color:#fff; border:none; border-radius:999px; padding:8px 16px; font-size:13px; font-weight:700; cursor:pointer; z-index:9; }
  #legend { position:fixed; top:50%; left:16px; transform:translateY(-50%); display:flex; flex-direction:column; gap:16px; z-index:9; }
  #legend button { border:none; border-radius:999px; padding:6px 14px; font-size:12px; font-weight:600; cursor:pointer; color:#0b1020; opacity:0.85; }
  #legend button.active { outline:2px solid #fff; opacity:1; }
  #hint { position:fixed; bottom:8px; left:0; width:100%; text-align:center; color:#94a3b8; font-size:12px; pointer-events:none; }
</style>
</head>
<body>
<div id="tip"></div>
<div id="focus_header"></div>
<button id="back_btn" onclick="resetFocus()">← Back to the dome</button>
<button id="full_btn" onclick="toggleFull()">Full constellation</button>
<div id="legend"></div>
<div id="hint">Drag to rotate · scroll to zoom · click a level to highlight · click an entity for its constellation</div>
<script>
const DATA = __DATA__;

const LEVEL_COLORS = {L1:"#E0C04B", L2:"#00B0FF", L3:"#00E676", L4:"#E040FB", L5:"#FF6D00"};
const LEVEL_NAMES = {L1:"L1 modalities", L2:"L2 subtypes", L3:"L3 triggers", L4:"L4 Functional/contextual", L5:"L5 Generic/umbrella/taxon"};

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1020);
const camera = new THREE.PerspectiveCamera(58, window.innerWidth/window.innerHeight, 0.1, 200);
camera.position.set(0, 1.2, 7.2);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(window.devicePixelRatio || 1);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 2.0;
controls.maxDistance = 16;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.35;

function glowTexture(rgb, alpha) {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(32,32,0,32,32,32);
  g.addColorStop(0, 'rgba(255,255,255,'+(alpha||0.95)+')');
  g.addColorStop(0.35, 'rgba('+rgb+','+(alpha||0.9)+')');
  g.addColorStop(1, 'rgba('+rgb+',0)');
  ctx.fillStyle = g; ctx.fillRect(0,0,64,64);
  return new THREE.CanvasTexture(c);
}
const hexToRgb = (h) => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)].join(',');

const shell = new THREE.Mesh(
  new THREE.SphereGeometry(3, 48, 32),
  new THREE.MeshBasicMaterial({color:0x334155, wireframe:true, transparent:true, opacity:0.12})
);
scene.add(shell);

// entity sprites + positions
const entitySprites = [];
const entityByName = {};
const entityPos = {};
const N = DATA.entities.length;
for (let i = 0; i < N; i++) {
  const y = 1 - (i / (N - 1)) * 2;
  const r = Math.sqrt(1 - y*y);
  const th = Math.PI * (3 - Math.sqrt(5)) * i;
  const e = DATA.entities[i];
  const col = LEVEL_COLORS[e.level];
  const x = Math.cos(th)*r*3, yy = y*3, z = Math.sin(th)*r*3;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture(hexToRgb(col)), color: col, transparent:true, depthTest:false
  }));
  sprite.position.set(x, yy, z);
  const s = e.level === "L1" ? 0.6 : 0.42;
  sprite.scale.set(s, s, 1);
  sprite.userData = {kind:'entity', ...e};
  scene.add(sprite);
  entitySprites.push(sprite);
  entityByName[e.name] = sprite;
  entityPos[e.name] = {x: x, y: yy, z: z};
}

// full gene positions (all 9,265)
const genePositions = new Float32Array(DATA.genes.length * 3);
for (let i = 0; i < DATA.genes.length; i++) {
  const th = 2*Math.PI*Math.random(), phi = Math.acos(2*Math.random()-1);
  const rad = 2.4 + 0.5 * Math.random();
  genePositions[i*3]   = rad*Math.sin(phi)*Math.cos(th);
  genePositions[i*3+1] = rad*Math.sin(phi)*Math.sin(th);
  genePositions[i*3+2] = rad*Math.cos(phi);
}

function buildMainPoints(indices, size) {
  const pos = new Float32Array(indices.length * 3);
  indices.forEach((gi, k) => {
    pos[k*3] = genePositions[gi*3]; pos[k*3+1] = genePositions[gi*3+1]; pos[k*3+2] = genePositions[gi*3+2];
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({
    map: glowTexture('226,232,240'), color: 0xe2e8f0, size: size,
    transparent:true, depthTest:false, sizeAttenuation:true, opacity:0.85
  }));
  pts.userData = {indices: indices};
  return pts;
}

function buildThreads(indices, color, opacity) {
  const pos = [];
  for (const gi of indices) {
    const ep = entityPos[DATA.genes[gi].top];
    if (!ep) continue;
    pos.push(genePositions[gi*3], genePositions[gi*3+1], genePositions[gi*3+2], ep.x, ep.y, ep.z);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  return new THREE.LineSegments(g, new THREE.LineBasicMaterial({color: color, transparent:true, opacity: opacity}));
}

// default: sampled 400
const allIndices = DATA.genes.map((_, i) => i);
let currentIndices = DATA.sampled.slice();
let mainGenePoints = buildMainPoints(currentIndices, 0.26);
scene.add(mainGenePoints);
let threads = buildThreads(currentIndices, 0x475569, 0.1);
scene.add(threads);

function rebuildMain(indices, size) {
  scene.remove(mainGenePoints);
  scene.remove(threads);
  currentIndices = indices;
  mainGenePoints = buildMainPoints(indices, size);
  scene.add(mainGenePoints);
  threads = buildThreads(indices, 0x475569, 0.1);
  scene.add(threads);
  activeGenePoints = mainGenePoints;
  resetLevel();
}

let fullMode = false;
function toggleFull() {
  fullMode = !fullMode;
  rebuildMain(fullMode ? allIndices : DATA.sampled.slice(), fullMode ? 0.10 : 0.26);
  document.getElementById('full_btn').textContent = fullMode ? 'Sampled view' : 'Full constellation';
}

// fresh compact cloud for focus / level views
function buildCloudPoints(indices, size, opacity) {
  const pos = new Float32Array(indices.length * 3);
  let seed = 12345;
  const rnd = () => (seed = (seed*16807)%2147483647)/2147483647;
  for (let k = 0; k < indices.length; k++) {
    const th = 2*Math.PI*rnd(), phi = Math.acos(2*rnd()-1);
    const rad = 2.6 * Math.cbrt(rnd());
    pos[k*3]   = rad*Math.sin(phi)*Math.cos(th);
    pos[k*3+1] = rad*Math.sin(phi)*Math.sin(th);
    pos[k*3+2] = rad*Math.cos(phi);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({
    map: glowTexture('226,232,240'), color: 0xe2e8f0, size: size,
    transparent:true, depthTest:false, sizeAttenuation:true, opacity:opacity
  }));
  pts.userData = {indices: indices};
  return pts;
}

let activeGenePoints = mainGenePoints;
let levelGenePoints = null;
let levelThreads = null;
let activeLevel = null;
let focusPoints = null;
let focusedEntity = null;

function highlightLevel(lvl) {
  if (activeLevel === lvl) { resetLevel(); return; }
  resetLevel();
  activeLevel = lvl;
  entitySprites.forEach(s => { s.material.opacity = (s.userData.level === lvl) ? 1 : 0.1; });
  mainGenePoints.material.opacity = 0.05;
  threads.material.opacity = 0.02;
  const idxs = DATA.level_genes[lvl] || [];
  levelGenePoints = buildCloudPoints(idxs, 0.26, 0.95);
  scene.add(levelGenePoints);
  levelThreads = buildThreads(idxs, LEVEL_COLORS[lvl], 0.25);
  scene.add(levelThreads);
  activeGenePoints = levelGenePoints;
  document.querySelectorAll('#legend button').forEach(b => b.classList.toggle('active', b.dataset.level === lvl));
}
function resetLevel() {
  activeLevel = null;
  entitySprites.forEach(s => { s.material.opacity = 1; });
  mainGenePoints.material.opacity = 0.85;
  threads.material.opacity = 0.1;
  if (levelGenePoints) { scene.remove(levelGenePoints); levelGenePoints = null; }
  if (levelThreads) { scene.remove(levelThreads); levelThreads = null; }
  activeGenePoints = mainGenePoints;
  document.querySelectorAll('#legend button').forEach(b => b.classList.remove('active'));
}

function focusEntity(name) {
  resetLevel();
  resetFocus();
  focusedEntity = name;
  const idxs = DATA.entity_genes[name] || [];
  focusPoints = buildCloudPoints(idxs, 0.26, 0.95);
  scene.add(focusPoints);
  activeGenePoints = focusPoints;
  mainGenePoints.visible = false;
  threads.visible = false;
  shell.visible = false;
  entitySprites.forEach(s => { s.material.opacity = 0.1; });
  const e = entityByName[name].userData;
  document.getElementById('focus_header').innerHTML =
    '<b><i>' + e.name + '</i></b> · ' + e.n + ' genes · <span style="color:' + LEVEL_COLORS[e.level] + '">' + LEVEL_NAMES[e.level] + '</span>';
  document.getElementById('focus_header').style.display = 'block';
  document.getElementById('back_btn').style.display = 'block';
}
function resetFocus() {
  focusedEntity = null;
  if (focusPoints) { scene.remove(focusPoints); focusPoints = null; }
  mainGenePoints.visible = true;
  threads.visible = true;
  shell.visible = true;
  entitySprites.forEach(s => { s.material.opacity = 1; });
  activeGenePoints = mainGenePoints;
  document.getElementById('focus_header').style.display = 'none';
  document.getElementById('back_btn').style.display = 'none';
}

(function buildLegend() {
  const leg = document.getElementById('legend');
  ['L1','L2','L3','L4','L5'].forEach(lvl => {
    const b = document.createElement('button');
    b.textContent = LEVEL_NAMES[lvl] + ' (' + (DATA.level_counts[lvl]||0) + ')';
    b.style.background = LEVEL_COLORS[lvl];
    b.dataset.level = lvl;
    b.onclick = () => highlightLevel(lvl);
    leg.appendChild(b);
  });
})();

const raycaster = new THREE.Raycaster();
raycaster.params.Points.threshold = 0.1;
const mouse = new THREE.Vector2();
const tip = document.getElementById('tip');
let hovered = null;

function resolveGeneIndex(points, hitIndex) {
  const idxs = points.userData.indices;
  return idxs ? idxs[hitIndex] : hitIndex;
}

function onMouseMove(e) {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);

  const eHits = raycaster.intersectObjects(entitySprites);
  if (eHits.length && !focusedEntity) {
    const d = eHits[0].object.userData;
    tip.style.display = 'block';
    tip.style.left = (e.clientX + 14) + 'px';
    tip.style.top = (e.clientY + 14) + 'px';
    tip.innerHTML = '<b>' + d.name + '</b><br><span style="color:' + LEVEL_COLORS[d.level] + '">' + LEVEL_NAMES[d.level] + '</span> · ' + d.n + ' genes<br><span style="color:#a8a29e">click for its constellation</span>';
    hovered = {kind:'entity', data:d};
    return;
  }
  const gHits = raycaster.intersectObject(activeGenePoints);
  if (gHits.length && gHits[0].index != null) {
    const gi = resolveGeneIndex(activeGenePoints, gHits[0].index);
    const g = DATA.genes[gi];
    const ctx = focusedEntity ? ('in <span style="color:#FF9800">' + focusedEntity + '</span>') : 'trail';
    tip.style.display = 'block';
    tip.style.left = (e.clientX + 14) + 'px';
    tip.style.top = (e.clientY + 14) + 'px';
    tip.innerHTML = '<b><i>' + g.symbol + '</i></b> · ' + g.n + ' RCD entities<br><span style="color:#a8a29e">click for its evidence ' + ctx + '</span>';
    hovered = {kind:'gene', data:g};
    return;
  }
  tip.style.display = 'none'; hovered = null;
}

function onClick() {
  if (!hovered) return;
  if (hovered.kind === 'entity') {
    focusEntity(hovered.data.name);
  } else if (hovered.kind === 'gene') {
    const entity = focusedEntity || hovered.data.top;
    window.parent.Shiny.setInputValue('dome3d_gene', hovered.data.symbol + '|' + entity, {priority:'event'});
  }
}

window.addEventListener('mousemove', onMouseMove);
renderer.domElement.addEventListener('click', onClick);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
"""

html = TEMPLATE.replace('__DATA__', json.dumps(DATA, ensure_ascii=False))
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print('entities:', len(entity_list), '| all genes:', len(genes), '| sampled:', len(sampled))
print('wrote', OUT, '|', len(html), 'bytes')
