import * as THREE from 'three';
import './style.css';

const $ = (s) => document.querySelector(s);
const state = { nodes: [], edges: [], selected: null, conversationId: crypto.randomUUID(), recognition: null, speaking: false };
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(52, innerWidth / innerHeight, .1, 100);
camera.position.set(0, 0, 9);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(innerWidth, innerHeight);
$('#galaxy').append(renderer.domElement);
const graph = new THREE.Group(); scene.add(graph);
const stars = new THREE.BufferGeometry(), starPositions = new Float32Array(1400 * 3);
for (let i = 0; i < starPositions.length; i += 3) { const r = 4 + Math.random() * 13; const a = Math.random() * Math.PI * 2; starPositions[i] = Math.cos(a) * r; starPositions[i + 1] = (Math.random() - .5) * 5; starPositions[i + 2] = Math.sin(a) * r; }
stars.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
scene.add(new THREE.Points(stars, new THREE.PointsMaterial({ color: 0x243862, size: .018 })));
const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();

function drawGraph(data) {
  state.nodes = data.nodes || []; state.edges = data.edges || [];
  graph.clear();
  const positions = new Map();
  state.nodes.forEach((node, i) => {
    const a = i / Math.max(state.nodes.length, 1) * Math.PI * 2;
    const r = 1.2 + (i % 5) * .45;
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(.11 + (i % 3) * .025, 16, 12),
      new THREE.MeshBasicMaterial({ color: node.kind === 'memory' ? 0x70e8ff : 0xb287ff }));
    mesh.position.set(Math.cos(a) * r, Math.sin(a) * r * .65, (i % 4) * .12);
    mesh.userData = node; positions.set(node.id, mesh.position); graph.add(mesh);
  });
  const linePositions = [];
  state.edges.forEach((edge) => { const a = positions.get(edge.source), b = positions.get(edge.target); if (a && b) linePositions.push(a.x,a.y,a.z,b.x,b.y,b.z); });
  if (linePositions.length) { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3)); graph.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0x263d73, transparent: true, opacity: .6 }))); }
  $('#stats').textContent = `${state.nodes.length} memories · ${state.edges.length} connections`;
}
function focus(node) {
  state.selected = node;
  $('#nodeDetail').innerHTML = `<strong>${escapeHtml(node.label)}</strong><br><small>${escapeHtml(node.id)}</small><br><br>Click a citation to focus this memory.`;
  const object = graph.children.find((child) => child.userData?.id === node.id);
  if (object) { object.material.color.set(0xffffff); camera.position.lerp(new THREE.Vector3(object.position.x * .3, object.position.y * .3, 6), .4); }
}
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c])); }
async function api(path, options) { const response = await fetch(path, options); if (!response.ok) throw new Error(await response.text()); return response.json(); }
async function loadGraph() { try { drawGraph(await api('/api/graph')); $('#health').textContent = 'ONLINE'; } catch { $('#health').textContent = 'OFFLINE'; } }
async function loadConfig() {
  try { const [p, personality, tools] = await Promise.all([api('/api/provider'), api('/api/personality'), api('/api/tools')]);
    $('#provider').value = p.provider; $('#model').value = p.model; $('#personality').textContent = `${personality.name}: ${personality.system_prompt}`;
    $('#toolList').innerHTML = tools.map(t => `<button class="tool" data-tool="${escapeHtml(t.name)}">${escapeHtml(t.name)}${t.requires_confirmation ? ' · approval' : ''}</button>`).join('');
    document.querySelectorAll('.tool').forEach(b => b.onclick = () => requestTool(b.dataset.tool));
  } catch { $('#personality').textContent = 'Configuration unavailable'; }
}
function renderSources(sources = []) { $('#citations').innerHTML = sources.map(s => `<button class="citation" data-id="${escapeHtml(s.id)}">◈ ${escapeHtml(s.source)} · ${escapeHtml(s.metadata?.heading || 'memory')}</button>`).join(''); document.querySelectorAll('.citation').forEach(b => b.onclick = () => { const n = state.nodes.find(x => x.id === b.dataset.id); if (n) focus(n); }); }
async function ask() {
  const question = $('#query').value.trim(); if (!question) return;
  stopVoice(); $('#answer').textContent = ''; renderSources(); $('#streamState').textContent = 'TRANSMITTING · 0%';
  try {
    const response = await fetch('/api/ask/stream', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ question, conversation_id: state.conversationId, stream: true }) });
    if (!response.ok || !response.body) throw new Error('stream unavailable');
    const reader = response.body.getReader(), decoder = new TextDecoder(); let buffer = '';
    while (true) { const { value, done } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const events = buffer.split('\n\n'); buffer = events.pop(); for (const event of events) { const line = event.split('\n').find(x => x.startsWith('data:')); if (!line) continue; const payload = JSON.parse(line.slice(5)); if (payload.token) $('#answer').textContent += payload.token; if (payload.done) { renderSources(payload.sources); $('#streamState').textContent = 'COMPLETE'; speak($('#answer').textContent); } } }
  } catch (error) { $('#streamState').textContent = `ERROR · ${error.message}`; }
}
function stopVoice() { if (state.recognition) { state.recognition.onresult = null; state.recognition.stop(); state.recognition = null; } speechSynthesis.cancel(); state.speaking = false; }
function speak(text) { if (!text || !('speechSynthesis' in window)) return; speechSynthesis.cancel(); const utterance = new SpeechSynthesisUtterance(text); utterance.onstart = () => state.speaking = true; utterance.onend = () => state.speaking = false; speechSynthesis.speak(utterance); }
function startVoice() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition; if (!Recognition) { $('#streamState').textContent = 'VOICE API UNSUPPORTED'; return; }
  stopVoice(); const recognition = new Recognition(); recognition.interimResults = true; recognition.continuous = $('#wake').checked;
  recognition.onresult = (event) => { const transcript = [...event.results].map(r => r[0].transcript).join(''); $('#query').value = transcript; if (event.results[event.results.length - 1].isFinal && !$('#wake').checked) ask(); };
  recognition.onend = () => { state.recognition = null; if ($('#wake').checked) startVoice(); }; recognition.onerror = () => { state.recognition = null; }; state.recognition = recognition; recognition.start(); $('#streamState').textContent = $('#wake').checked ? 'WAKE LISTENING' : 'LISTENING · SPEAK NOW';
}
async function requestTool(name) { $('#approval').classList.remove('hidden'); $('#approvalText').textContent = `Jarvis wants to run “${name}”. Review and approve this action.`; $('#approve').onclick = async () => { $('#approval').classList.add('hidden'); try { const result = await api('/api/tools/execute', { method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({ name, arguments:{}, confirmed:true }) }); $('#streamState').textContent = result.ok ? 'TOOL COMPLETE' : `TOOL ERROR · ${result.error}`; } catch (e) { $('#streamState').textContent = `TOOL ERROR · ${e.message}`; } }; }
$('#ask').onclick = ask; $('#query').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); } }); $('#voice').onclick = startVoice; $('#settingsToggle').onclick = () => $('#settings').classList.toggle('hidden'); $('#deny').onclick = () => $('#approval').classList.add('hidden');
$('#wake').onchange = () => $('#wake').checked ? startVoice() : stopVoice();
$('#saveProvider').onclick = async () => { try { const result = await api('/api/provider', { method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({ provider:$('#provider').value, model:$('#model').value }) }); $('#streamState').textContent = `MODEL ACTIVE · ${result.provider}/${result.model}`; } catch (e) { $('#streamState').textContent = `MODEL ERROR · ${e.message}`; } };
$('#indexNotes').onclick = async () => { $('#indexStatus').textContent = 'Indexing…'; try { const result = await api('/api/index/path', { method:'POST', headers:{'content-type':'application/json'}, body:'{}' }); $('#indexStatus').textContent = `${result.chunks} chunks indexed`; await loadGraph(); } catch (e) { $('#indexStatus').textContent = `Index error: ${e.message}`; } };
renderer.domElement.addEventListener('pointerdown', event => { pointer.x = (event.clientX / innerWidth) * 2 - 1; pointer.y = -(event.clientY / innerHeight) * 2 + 1; raycaster.setFromCamera(pointer, camera); const hit = raycaster.intersectObjects(graph.children).find(x => x.object.userData?.id); if (hit) focus(hit.object.userData); });
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
function animate() { requestAnimationFrame(animate); graph.rotation.y += .0007; renderer.render(scene, camera); } animate(); loadGraph(); loadConfig();
