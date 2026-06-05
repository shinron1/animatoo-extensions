# -*- coding: utf-8 -*-
import json, os, re, subprocess, webbrowser, threading, urllib.parse, sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

WORKDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(WORKDIR, "repo")
HOST, PORT = "127.0.0.1", 8765
if not os.path.isdir(REPO_DIR): os.makedirs(REPO_DIR)

METADATA_KEYS = ["name", "version", "author", "lang", "license", "icon", "package", "type", "webSite", "description", "nsfw", "tags"]
META_LABELS = {"name":"الاسم","version":"الإصدار","author":"المطور","lang":"اللغة","license":"الترخيص","icon":"الأيقونة","package":"الحزمة","type":"النوع","webSite":"الموقع","description":"الوصف","nsfw":"+18","tags":"وسوم"}

HTML = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>مدير إضافات Miru | Miru Extensions</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root {
  --primary: #6c5ce7;
  --primary-hover: #a29bfe;
  --secondary: #00cec9;
  --dark: #0f111a;
  --darker: #090a0f;
  --card-bg: rgba(25, 28, 41, 0.7);
  --card-border: rgba(255, 255, 255, 0.1);
  --text: #f1f2f6;
  --text-muted: #a4b0be;
  --danger: #ff4757;
  --success: #2ed573;
  --warning: #ffa502;
  --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
body {
  background: var(--darker);
  color: var(--text);
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}
/* Animated Background */
body::before {
  content: '';
  position: fixed;
  top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 50% 50%, rgba(108, 92, 231, 0.15), transparent 40%),
              radial-gradient(circle at 80% 20%, rgba(0, 206, 201, 0.1), transparent 30%);
  animation: bg-pulse 15s ease-in-out infinite alternate;
  z-index: -1;
}
@keyframes bg-pulse { 0% { transform: scale(1); } 100% { transform: scale(1.1); } }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--darker); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.4); }

.container { max-width: 1400px; margin: 0 auto; padding: 20px; }

/* Header */
.header {
  display: flex; justify-content: space-between; align-items: center;
  background: var(--card-bg); backdrop-filter: blur(10px);
  border: 1px solid var(--card-border); border-radius: 16px;
  padding: 20px 30px; margin-bottom: 25px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.header h1 {
  font-size: 24px; font-weight: 800;
  background: linear-gradient(135deg, #a29bfe, #00cec9);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  display: flex; align-items: center; gap: 12px;
}
.header h1 i { -webkit-text-fill-color: initial; color: #a29bfe; font-size: 28px; }
.status {
  background: rgba(46, 213, 115, 0.1); color: var(--success);
  padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600;
  border: 1px solid rgba(46, 213, 115, 0.2);
}

/* Toolbar */
.toolbar {
  display: flex; flex-wrap: wrap; gap: 15px; align-items: center;
  background: var(--card-bg); backdrop-filter: blur(10px);
  border: 1px solid var(--card-border); border-radius: 16px;
  padding: 15px 20px; margin-bottom: 25px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.btn {
  background: rgba(255,255,255,0.05); color: var(--text);
  border: 1px solid var(--card-border); border-radius: 10px;
  padding: 10px 20px; font-size: 14px; font-weight: 600; cursor: pointer;
  display: flex; align-items: center; gap: 8px; transition: var(--transition);
}
.btn:hover { background: rgba(255,255,255,0.1); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
.btn.primary { background: var(--primary); border-color: var(--primary); }
.btn.primary:hover { background: var(--primary-hover); box-shadow: 0 5px 20px rgba(108,92,231,0.4); }
.btn.success { background: var(--success); border-color: var(--success); color: #000; }
.btn.success:hover { background: #26b260; box-shadow: 0 5px 20px rgba(46,213,115,0.4); }

.search-wrap {
  display: flex; align-items: center; gap: 15px; margin-right: auto;
  background: rgba(0,0,0,0.2); border-radius: 10px; padding: 5px 15px;
  border: 1px solid var(--card-border);
}
.search-wrap i { color: var(--text-muted); }
.search-wrap input[type=text] {
  background: transparent; border: none; color: var(--text);
  padding: 8px 0; font-size: 14px; width: 220px; outline: none;
}
.search-wrap input::placeholder { color: var(--text-muted); }
.toolbar label {
  display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 14px; color: var(--text-muted);
  user-select: none; transition: var(--transition);
}
.toolbar label:hover { color: var(--text); }
.toolbar label input { accent-color: var(--primary); width: 16px; height: 16px; cursor: pointer; }

/* Table */
.table-wrap {
  background: var(--card-bg); backdrop-filter: blur(10px);
  border: 1px solid var(--card-border); border-radius: 16px;
  overflow-x: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
table { width: 100%; border-collapse: separate; border-spacing: 0; }
thead { background: rgba(0,0,0,0.3); }
th {
  padding: 18px 20px; font-size: 14px; font-weight: 600; color: var(--text-muted);
  text-align: right; cursor: pointer; user-select: none; transition: var(--transition);
  border-bottom: 1px solid var(--card-border);
}
th:hover { color: var(--text); background: rgba(255,255,255,0.05); }
th i { font-size: 12px; margin-right: 5px; opacity: 0.5; }
td {
  padding: 16px 20px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.05);
  transition: var(--transition); vertical-align: middle;
}
tr:hover td { background: rgba(255,255,255,0.03); }
tr:last-child td { border-bottom: none; }
tr.nsfw td { color: #ff9ff3; }

.badge { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; }
.badge-safe { background: rgba(46, 213, 115, 0.15); color: var(--success); border: 1px solid rgba(46,213,115,0.3); }
.badge-type { background: rgba(108, 92, 231, 0.15); color: #a29bfe; border: 1px solid rgba(108,92,231,0.3); }

.actions { display: flex; gap: 8px; }
.btn-icon {
  width: 32px; height: 32px; border-radius: 8px; border: none; cursor: pointer;
  display: flex; justify-content: center; align-items: center; font-size: 14px;
  transition: var(--transition); color: #fff;
}
.btn-icon.edit { background: rgba(108, 92, 231, 0.2); color: var(--primary-hover); }
.btn-icon.edit:hover { background: var(--primary); color: #fff; transform: scale(1.1); }
.btn-icon.delete { background: rgba(255, 71, 87, 0.2); color: var(--danger); }
.btn-icon.delete:hover { background: var(--danger); color: #fff; transform: scale(1.1); }

.empty { text-align: center; padding: 80px 20px; color: var(--text-muted); font-size: 18px; display: none; }
.empty i { font-size: 48px; margin-bottom: 15px; opacity: 0.5; display: block; }

/* Modal */
.modal {
  display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); z-index: 1000;
  justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s;
}
.modal.show { display: flex; opacity: 1; }
.modal-content {
  background: var(--dark); border: 1px solid var(--card-border);
  border-radius: 20px; width: 95%; max-width: 1000px; height: 90vh;
  display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  transform: scale(0.95); transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.modal.show .modal-content { transform: scale(1); }

.modal-header {
  padding: 20px 25px; border-bottom: 1px solid var(--card-border);
  display: flex; justify-content: space-between; align-items: center;
}
.modal-header h2 { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.modal-header button {
  background: rgba(255,255,255,0.1); border: none; color: var(--text);
  width: 36px; height: 36px; border-radius: 50%; cursor: pointer;
  display: flex; justify-content: center; align-items: center; transition: var(--transition);
}
.modal-header button:hover { background: var(--danger); transform: rotate(90deg); }

.modal-body { padding: 0; overflow: hidden; flex: 1; display: flex; flex-direction: column; }

.tabs {
  display: flex; background: rgba(0,0,0,0.2); border-bottom: 1px solid var(--card-border);
}
.tab {
  padding: 15px 25px; cursor: pointer; font-size: 15px; font-weight: 600; color: var(--text-muted);
  transition: var(--transition); border-bottom: 3px solid transparent; display: flex; align-items: center; gap: 8px;
}
.tab.active { color: var(--primary-hover); border-bottom-color: var(--primary); background: rgba(255,255,255,0.02); }
.tab:hover:not(.active) { color: var(--text); background: rgba(255,255,255,0.05); }

.tab-content { display: none; padding: 25px; flex: 1; overflow-y: auto; }
.tab-content.active { display: block; animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Form */
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 13px; color: var(--text-muted); font-weight: 600; margin-right: 5px; }
.form-group input, .form-group textarea {
  background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1);
  color: var(--text); padding: 12px 15px; border-radius: 10px; font-size: 14px;
  transition: var(--transition); width: 100%;
}
.form-group input:focus, .form-group textarea:focus {
  border-color: var(--primary); background: rgba(0,0,0,0.4);
  box-shadow: 0 0 0 3px rgba(108,92,231,0.2); outline: none;
}
.form-group textarea { font-family: 'JetBrains Mono', monospace; height: 100%; min-height: 400px; resize: none; }
#code-tab { padding: 0; }
#code-tab .form-group.full { height: 100%; padding: 20px; }

.modal-footer {
  padding: 20px 25px; border-top: 1px solid var(--card-border);
  display: flex; justify-content: flex-end; gap: 15px; background: rgba(0,0,0,0.2);
}

/* Toast */
.toast {
  position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%) translateY(50px);
  background: var(--card-bg); backdrop-filter: blur(10px); border: 1px solid var(--card-border);
  color: var(--text); padding: 15px 25px; border-radius: 12px; font-size: 15px; font-weight: 600;
  z-index: 2000; opacity: 0; transition: var(--transition); pointer-events: none;
  box-shadow: 0 15px 30px rgba(0,0,0,0.4); display: flex; align-items: center; gap: 10px;
}
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
.toast.error { border-bottom: 3px solid var(--danger); }
.toast.success { border-bottom: 3px solid var(--success); }
.toast i { font-size: 20px; }
.toast.error i { color: var(--danger); }
.toast.success i { color: var(--success); }

@media(max-width: 900px) {
  .toolbar { flex-direction: column; align-items: stretch; }
  .search-wrap { margin-right: 0; width: 100%; }
  .search-wrap input[type=text] { width: 100%; }
}
</style>
</head>
<body>
<div class="container">
<div class="header">
  <h1><i class="fa-solid fa-box-open"></i> مدير إضافات Miru</h1>
  <span class="status" id="status"><i class="fa-solid fa-circle-notch fa-spin"></i> جاري التحميل...</span>
</div>

<div class="toolbar">
  <button class="btn" onclick="loadExtensions()"><i class="fa-solid fa-rotate-right"></i> تحديث</button>
  <button class="btn primary" onclick="openNew()"><i class="fa-solid fa-plus"></i> إضافة جديدة</button>
  <button class="btn" onclick="document.getElementById('fileInput').click()"><i class="fa-solid fa-file-import"></i> استيراد ملف</button>
  <input type="file" id="fileInput" accept=".js" style="display:none" onchange="importFile(event)">
  <button class="btn" onclick="generateFiles()"><i class="fa-solid fa-boxes-packing"></i> توليد الملفات</button>
  <button class="btn success" onclick="gitPush()"><i class="fa-brands fa-github"></i> رفع إلى GitHub</button>
  <div class="search-wrap">
    <i class="fa-solid fa-magnifying-glass"></i>
    <input type="text" id="search" placeholder="ابحث عن إضافة..." oninput="filterList()">
    <label><input type="checkbox" id="showNsfw" onchange="filterList()"> إظهار +18</label>
  </div>
</div>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th onclick="sortBy('name')">الاسم <i class="fa-solid fa-sort"></i></th>
        <th onclick="sortBy('package')">الحزمة <i class="fa-solid fa-sort"></i></th>
        <th onclick="sortBy('version')">الإصدار <i class="fa-solid fa-sort"></i></th>
        <th onclick="sortBy('author')">المطور <i class="fa-solid fa-sort"></i></th>
        <th onclick="sortBy('lang')">اللغة <i class="fa-solid fa-sort"></i></th>
        <th onclick="sortBy('type')">النوع <i class="fa-solid fa-sort"></i></th>
        <th>+18</th>
        <th style="text-align:center">إجراءات</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>
  <div class="empty" id="empty"><i class="fa-solid fa-folder-open"></i><br>لا توجد إضافات تطابق بحثك</div>
</div>
</div>

<div class="modal" id="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h2 id="modalTitle"><i class="fa-solid fa-pen-to-square"></i> إضافة جديدة</h2>
      <button onclick="closeModal()"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="modal-body">
      <div class="tabs">
        <div class="tab active" onclick="switchTab(this,'meta-tab')"><i class="fa-solid fa-clipboard-list"></i> البيانات الوصفية</div>
        <div class="tab" onclick="switchTab(this,'code-tab')"><i class="fa-solid fa-code"></i> الكود البرمجي</div>
      </div>
      <div class="tab-content active" id="meta-tab">
        <div class="form-grid" id="metaGrid"></div>
      </div>
      <div class="tab-content" id="code-tab">
        <div class="form-group full">
          <textarea id="codeEditor" spellcheck="false"></textarea>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn" onclick="closeModal()">إلغاء</button>
      <button class="btn primary" onclick="saveExtension()"><i class="fa-solid fa-floppy-disk"></i> حفظ الإضافة</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let extensions = [], editingUrl = null, sortCol = null, sortAsc = true;

const metaKeys = ["name","version","author","lang","license","icon","package","type","webSite","description","nsfw","tags"];
const metaLabels = {"name":"الاسم","version":"الإصدار","author":"المطور","lang":"اللغة","license":"الترخيص","icon":"الأيقونة","package":"الحزمة","type":"النوع","webSite":"الموقع","description":"الوصف","nsfw":"+18","tags":"وسوم"};
const metaPlaceholders = {"name":"مثال: MyExtension","version":"v0.0.1","author":"اسم المطور","license":"MIT","icon":"رابط الأيقونة","webSite":"رابط الموقع","description":"وصف مختصر"};

function toast(msg,type=''){
  const t=document.getElementById('toast');
  t.innerHTML = `<i class="fa-solid ${type==='error'?'fa-circle-exclamation':'fa-circle-check'}"></i> ${msg}`;
  t.className='toast show'+(type?' '+type:'');
  setTimeout(()=>t.className='toast',3000);
}

async function api(method,path,body){
  const opts={method,headers:{}};
  if(body){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(body)}
  const r=await fetch('/api'+path,opts);
  const d=await r.json();
  if(!r.ok){toast(d.error||'خطأ','error');throw new Error(d.error)}
  return d
}

function setStatus(msg, icon=''){
  document.getElementById('status').innerHTML = icon ? `<i class="${icon}"></i> ${msg}` : msg;
}

async function loadExtensions(){
  setStatus('جاري التحميل...', 'fa-solid fa-circle-notch fa-spin');
  try{
    const data=await api('GET','/extensions');
    extensions=data;
    filterList();
    setStatus(data.length+' إضافة', 'fa-solid fa-check');
  }catch(e){setStatus('فشل التحميل', 'fa-solid fa-triangle-exclamation')}
}

function getNsfwEmoji(v){return v==='true'?'<span class="badge badge-type" style="background:rgba(255,71,87,0.15);color:var(--danger);border-color:rgba(255,71,87,0.3)">🔞 نعم</span>':'<span style="color:var(--text-muted)">لا</span>'}

function filterList(){
  const q=document.getElementById('search').value.toLowerCase();
  const showNsfw=document.getElementById('showNsfw').checked;
  const tbody=document.getElementById('tbody');
  const empty=document.getElementById('empty');
  tbody.innerHTML='';
  let filtered=extensions.filter(e=>(showNsfw||e.nsfw!=='true')&&(!q||Object.values(e).some(v=>String(v).toLowerCase().includes(q))));
  if(sortCol)filtered.sort((a,b)=>{
    let va=(a[sortCol]||'').toLowerCase(),vb=(b[sortCol]||'').toLowerCase();
    return sortAsc?va.localeCompare(vb):vb.localeCompare(va)
  });
  if(filtered.length===0){empty.style.display='block';return}
  empty.style.display='none';
  filtered.forEach(e=>{
    const tr=document.createElement('tr');
    if(e.nsfw==='true')tr.className='nsfw';
    tr.innerHTML=`
      <td><strong>${e.name||''}</strong></td>
      <td style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--text-muted)">${e.package||''}</td>
      <td><span class="badge badge-safe">${e.version||''}</span></td>
      <td>${e.author||''}</td>
      <td>${e.lang||''}</td>
      <td><span class="badge badge-type">${e.type||''}</span></td>
      <td>${getNsfwEmoji(e.nsfw)}</td>
      <td><div class="actions" style="justify-content:center">
        <button class="btn-icon edit" onclick="openEdit('${e.url}')" title="تعديل"><i class="fa-solid fa-pen"></i></button>
        <button class="btn-icon delete" onclick="deleteExt('${e.url}')" title="حذف"><i class="fa-solid fa-trash"></i></button>
      </div></td>
    `;
    tbody.appendChild(tr)
  })
}

function sortBy(col){
  if(sortCol===col)sortAsc=!sortAsc;else{sortCol=col;sortAsc=true}
  filterList()
}

async function deleteExt(url){
  if(!confirm('هل أنت متأكد من حذف '+url+'؟\\nلا يمكن التراجع عن هذا الإجراء.'))return;
  try{
    await api('DELETE','/extensions/'+encodeURIComponent(url));
    toast('تم حذف الإضافة بنجاح','success');
    loadExtensions()
  }catch(e){}
}

function switchTab(el,id){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(id).classList.add('active')
}

function buildMetaForm(meta){
  const grid=document.getElementById('metaGrid');
  grid.innerHTML='';
  metaKeys.forEach(key=>{
    const div=document.createElement('div');
    div.className='form-group'+(key==='description'?' full':'');
    div.innerHTML=`
      <label>${metaLabels[key]}</label>
      <input id="meta-${key}" placeholder="${metaPlaceholders[key]||''}" value="${(meta[key]||'').replace(/"/g,'&quot;')}">
    `;
    grid.appendChild(div)
  })
}

function openNew(){
  editingUrl=null;
  document.getElementById('modalTitle').innerHTML='<i class="fa-solid fa-square-plus"></i> إضافة جديدة';
  buildMetaForm({});
  document.getElementById('codeEditor').value='export default class extends Extension {\\n  async latest(page) {\\n    // your code here\\n  }\\n}';
  document.getElementById('modal').classList.add('show')
}

async function openEdit(url){
  editingUrl=url;
  document.getElementById('modalTitle').innerHTML='<i class="fa-solid fa-pen-to-square"></i> تعديل: <span style="color:var(--primary-hover);font-family:\\'JetBrains Mono\\',monospace;font-size:16px">'+url+'</span>';
  try{
    const data=await api('GET','/extensions/'+encodeURIComponent(url));
    buildMetaForm(data.meta);
    document.getElementById('codeEditor').value=data.code;
    document.getElementById('modal').classList.add('show')
  }catch(e){}
}

function closeModal(){document.getElementById('modal').classList.remove('show')}

async function saveExtension(){
  const meta={};
  metaKeys.forEach(key=>{const v=document.getElementById('meta-'+key).value.trim();if(v)meta[key]=v});
  const code=document.getElementById('codeEditor').value;
  if(!meta.name){toast('حقل الاسم مطلوب','error');return}
  if(!meta.package){toast('حقل الحزمة مطلوب','error');return}
  try{
    if(editingUrl){
      await api('PUT','/extensions/'+encodeURIComponent(editingUrl),{meta,code});
      toast('تم حفظ التعديلات بنجاح','success')
    }else{
      await api('POST','/extensions',{meta,code});
      toast('تم إنشاء الإضافة بنجاح','success')
    }
    closeModal();
    loadExtensions()
  }catch(e){}
}

async function importFile(event){
  const file=event.target.files[0];
  if(!file)return;
  const reader=new FileReader();
  reader.onload=async function(e){
    const b64=e.target.result.split(',')[1];
    try{
      const r=await fetch('/api/extensions/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data:b64,filename:file.name})});
      const d=await r.json();
      if(!r.ok){toast(d.error||'خطأ','error');return}
      toast('تم استيراد '+d.url+' بنجاح','success');
      loadExtensions()
    }catch(err){toast('فشل الاستيراد: '+err.message,'error')}
    document.getElementById('fileInput').value=''
  };
  reader.readAsDataURL(file)
}

async function generateFiles(){
  try{
    const r=await api('POST','/generate');
    toast(r.message,'success');
    setStatus(r.message, 'fa-solid fa-check-double')
  }catch(e){}
}

async function gitPush(){
  if(!confirm('هل أنت متأكد من رفع التغييرات إلى GitHub؟'))return;
  setStatus('جاري الرفع...', 'fa-solid fa-circle-notch fa-spin');
  try{
    const r=await api('POST','/git-push');
    toast(r.message,'success');
    setStatus(r.message, 'fa-solid fa-check')
  }catch(e){
    setStatus('فشل الرفع', 'fa-solid fa-triangle-exclamation')
  }
}

loadExtensions();
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        elif path.startswith("/api/extensions"):
            parts = path.split("/")
            if len(parts) == 3:
                self._list_extensions()
            elif len(parts) == 4:
                self._get_extension(parts[3])
            else:
                self._json_error(400, "Invalid path")
        else:
            self._json_error(404, "Not found")

    def do_POST(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            if path == "/api/extensions":
                self._create_extension()
            elif path == "/api/extensions/import":
                self._import_extension()
            elif path == "/api/generate":
                self._generate_files()
            elif path == "/api/git-push":
                self._git_push()
            else:
                self._json_error(404, "Not found")
        except Exception as e:
            self._json_error(500, f"خطأ داخلي: {e}")

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/extensions/"):
            url = urllib.parse.unquote(path.split("/")[-1])
            self._update_extension(url)
        else:
            self._json_error(404, "Not found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/extensions/"):
            url = urllib.parse.unquote(path.split("/")[-1])
            self._delete_extension(url)
        else:
            self._json_error(404, "Not found")

    def _read_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0: return {}
            raw = self.rfile.read(length)
            return json.loads(raw)
        except Exception as e:
            return {"_error": str(e)}

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _json_error(self, code, msg):
        self._json_response({"error": msg}, code)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _parse_extension(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            return None, None
        m = re.search(r'// ==MiruExtension==([\s\S]+?)// ==/MiruExtension==', content)
        if not m:
            return None, content
        meta = {"url": os.path.basename(filepath)}
        for line in m.group(1).split("\n"):
            line = line.strip()
            if line.startswith("// @"):
                parts = line[4:].split(" ", 1)
                if len(parts) == 2:
                    meta[parts[0]] = parts[1].strip()
        code = content[m.end():].strip()
        return meta, code

    def _generate_block(self, meta):
        lines = ["// ==MiruExtension=="]
        for key in METADATA_KEYS:
            if key == "tags": continue
            if key in meta and meta[key]:
                lines.append(f'// @{key:<10} {meta[key]}')
        lines.append("// ==/MiruExtension==\n")
        return "\n".join(lines)

    def _list_extensions(self):
        exts = []
        for fn in sorted(os.listdir(REPO_DIR)):
            if not fn.endswith(".js"): continue
            meta, _ = self._parse_extension(os.path.join(REPO_DIR, fn))
            if meta:
                exts.append(meta)
        self._json_response(exts)

    def _get_extension(self, url):
        fp = os.path.join(REPO_DIR, url)
        if not os.path.exists(fp) or not url.endswith(".js"):
            return self._json_error(404, "Not found")
        meta, code = self._parse_extension(fp)
        if not meta:
            return self._json_error(400, "Invalid extension")
        self._json_response({"meta": meta, "code": code or ""})

    def _create_extension(self):
        body = self._read_body()
        meta = body.get("meta", {})
        code = body.get("code", "")
        url = meta.get("package", "extension") + ".js"
        if not url.endswith(".js"): url += ".js"
        fp = os.path.join(REPO_DIR, url)
        if os.path.exists(fp):
            return self._json_error(409, "الملف موجود مسبقاً")
        content = self._generate_block(meta) + "\n" + code
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        self._json_response({"url": url, "message": "تم الإنشاء"})

    def _update_extension(self, url):
        fp = os.path.join(REPO_DIR, url)
        if not os.path.exists(fp):
            return self._json_error(404, "Not found")
        body = self._read_body()
        meta = body.get("meta", {})
        code = body.get("code", "")
        new_url = meta.get("package", "extension") + ".js"
        if not new_url.endswith(".js"): new_url += ".js"
        if new_url != url:
            os.remove(fp)
        fp = os.path.join(REPO_DIR, new_url)
        content = self._generate_block(meta) + "\n" + code
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        self._json_response({"url": new_url, "message": "تم الحفظ"})

    def _delete_extension(self, url):
        fp = os.path.join(REPO_DIR, url)
        if not os.path.exists(fp):
            return self._json_error(404, "Not found")
        os.remove(fp)
        self._json_response({"message": "تم الحذف"})

    def _import_extension(self):
        import base64
        body = self._read_body()
        if body.get("_error"):
            return self._json_error(400, f"خطأ في قراءة البيانات: {body['_error']}")
        try:
            raw = body.get("data", "")
            filename = body.get("filename", "extension.js")
            code = base64.b64decode(raw).decode("utf-8")
        except Exception as e:
            return self._json_error(400, f"خطأ في قراءة الملف: {e}")
        if not filename.endswith(".js"): filename += ".js"
        meta, _ = self._parse_extension_from_code(code, filename)
        if not meta:
            return self._json_error(400, "لم يتم العثور على بيانات MiruExtension في الملف")
        fp = os.path.join(REPO_DIR, filename)
        if os.path.exists(fp):
            base, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(os.path.join(REPO_DIR, f"{base}_{i}{ext}")):
                i += 1
            filename = f"{base}_{i}{ext}"
            fp = os.path.join(REPO_DIR, filename)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(code)
        self._json_response({"url": filename, "message": "تم الاستيراد"})

    def _parse_extension_from_code(self, code, filename):
        m = re.search(r'// ==MiruExtension==([\s\S]+?)// ==/MiruExtension==', code)
        if not m:
            return None, code
        meta = {"url": filename}
        for line in m.group(1).split("\n"):
            line = line.strip()
            if line.startswith("// @"):
                parts = line[4:].split(" ", 1)
                if len(parts) == 2:
                    meta[parts[0]] = parts[1].strip()
        return meta, code

    def _generate_files(self):
        extensions = []
        readme_lines = ["# Miru-Repo\n", "Miru extensions repository | [Miru App Download](https://github.com/miru-project/miru-app) |\n", "## List\n", "| Name | Package | Version | Author | Language | Type | Source |\n", "| ---- | ---- | --- | --- | --- | --- | --- |\n"]
        for fn in sorted(os.listdir(REPO_DIR)):
            if not fn.endswith(".js"): continue
            meta, _ = self._parse_extension(os.path.join(REPO_DIR, fn))
            if not meta: continue
            for k in ["description", "license", "tags"]: meta.pop(k, None)
            ext_data = {k: meta[k] for k in ["name", "version", "author", "lang", "license", "icon", "package", "type", "webSite", "description", "nsfw", "tags", "url"] if k in meta}
            extensions.append(ext_data)
            if meta.get("nsfw") != "true":
                url = f"https://github.com/shinron1/animatoo-extensions/blob/main/repo/{fn}"
                readme_lines.append(f"| {meta.get('name','')} | {meta.get('package','')} | {meta.get('version','')} | {meta.get('author','')} | {meta.get('lang','')} | {meta.get('type','')} | [Source Code]({url}) |\n")
        with open(os.path.join(WORKDIR, "index.json"), "w", encoding="utf-8") as f:
            json.dump(extensions, f, indent=1, ensure_ascii=False)
        with open(os.path.join(WORKDIR, "README.md"), "w", encoding="utf-8") as f:
            f.writelines(readme_lines)
        self._json_response({"message": f"تم توليد index.json و README.md ({len(extensions)} إضافة)"})

    def _git_push(self):
        try:
            subprocess.run(["git", "add", "-A"], cwd=WORKDIR, check=True, capture_output=True)
            result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=WORKDIR)
            has_changes = result.returncode != 0
            if has_changes:
                msg = f"تحديث الإضافات - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                subprocess.run(["git", "commit", "-m", msg], cwd=WORKDIR, check=True, capture_output=True)
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=WORKDIR, check=False, capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=WORKDIR, check=True, capture_output=True)
            self._json_response({"message": "تم الرفع إلى GitHub بنجاح"})
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode() if e.stderr else str(e)
            self._json_error(500, f"فشل الرفع: {err}")
        except FileNotFoundError:
            self._json_error(500, "Git غير مثبت")

def start_server():
    server = HTTPServer((HOST, PORT), Handler)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    webbrowser.open(f"http://{HOST}:{PORT}")
    print(f"Server running at: http://{HOST}:{PORT}")
    try:
        import time
        while True: time.sleep(3600)
    except KeyboardInterrupt:
        print("\nStopping server...")
