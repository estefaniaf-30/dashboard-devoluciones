"""
update_dashboard.py
Uso: python3 update_dashboard.py <ruta_al_csv>
Lee el CSV de devoluciones, genera index.html con el dashboard v5 y lo guarda en el mismo directorio.
"""
import sys, json, base64, csv, io, os, re

# ── LEER CSV ─────────────────────────────────────────────────────────────────
csv_path = sys.argv[1] if len(sys.argv) > 1 else None
if not csv_path:
    print("ERROR: Falta ruta al CSV. Uso: python3 update_dashboard.py <csv>")
    sys.exit(1)

with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
    raw = f.read()

reader = csv.DictReader(io.StringIO(raw))
headers = reader.fieldnames or []
print(f"Columnas encontradas: {headers}")

# Mapeo flexible de columnas
def find_col(headers, *candidates):
    for c in candidates:
        for h in headers:
            if c.lower() in h.lower():
                return h
    return None

col_fecha  = find_col(headers, 'fecha')
col_prod   = find_col(headers, 'producto')
col_det    = find_col(headers, 'curso', 'carrera', 'detalle', 'servicio')
col_tipo   = find_col(headers, 'tipo')
col_motivo = find_col(headers, 'motivo')
col_monto  = find_col(headers, 'monto', 'importe')
col_moneda = find_col(headers, 'moneda')
col_pais   = find_col(headers, 'pais', 'país')
col_plat   = find_col(headers, 'plataforma', '4.0')

print(f"Mapeo: fecha={col_fecha}, prod={col_prod}, det={col_det}, tipo={col_tipo}")
print(f"       motivo={col_motivo}, monto={col_monto}, moneda={col_moneda}, pais={col_pais}, plat={col_plat}")

def norm_fecha(s):
    s = (s or '').strip()
    # Intentar parsear varios formatos
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
        try:
            from datetime import datetime
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except:
            pass
    return s

def norm_prod(s):
    s = (s or '').strip().lower()
    if 'curso' in s: return 'curso'
    if 'carrera' in s: return 'carrera'
    if 'diploma' in s: return 'diplomatura'
    return s

EXCLUIR = {'penalidad', 'servicio', 'servicios', ''}

records = []
for row in reader:
    prod_raw = row.get(col_prod, '') if col_prod else ''
    prod = norm_prod(prod_raw)
    if prod in EXCLUIR:
        continue
    fecha = norm_fecha(row.get(col_fecha, '') if col_fecha else '')
    if not fecha.startswith('2026'):
        continue
    records.append({
        'f':  fecha,
        'p':  prod,
        'd':  (row.get(col_det, '') if col_det else '').strip(),
        't':  (row.get(col_tipo, '') if col_tipo else '').strip(),
        'm':  (row.get(col_motivo, '') if col_motivo else '').strip(),
        'mn': (row.get(col_monto, '') if col_monto else '').strip(),
        'mo': (row.get(col_moneda, '') if col_moneda else '').strip(),
        'pa': (row.get(col_pais, '') if col_pais else '').strip(),
        'pl': (row.get(col_plat, '') if col_plat else '').strip(),
    })

print(f"Registros 2026 validos: {len(records)}")

# ── GENERAR HTML ──────────────────────────────────────────────────────────────
DATA_JSON_STR = json.dumps(records, ensure_ascii=True)
DATA_JSON_STR_ESCAPED = DATA_JSON_STR.replace("'", "\\'")

pwd = 'efhfff30' + chr(33)
PASS_B64 = base64.b64encode(pwd.encode()).decode()

parts = []
parts.append("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Devoluciones 2026 - Coderhouse CX</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js"></script>
<style>
:root{--or:#F95B35;--pk:#E8197D;--dk:#1C0800;--gy:#9CA3AF;--bg:#FAF5EF;--sf:#FFFFFF;--bd:#EDE5DC;--tx:#1C0800;--t2:#9C8878;--ac:#FFF0E8}
@media(prefers-color-scheme:dark){:root{--bg:#130800;--sf:#1E0E00;--bd:#3A2010;--tx:#F5EDE5;--t2:#A08070;--ac:#2A1500}}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--tx);font-size:14px}
.hdr{background:#1C0800;padding:22px 32px;color:#fff;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}
.hdr .tag{font-size:10px;color:var(--or);text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:4px}
.hdr .ttl{font-size:24px;font-weight:800;letter-spacing:-.3px}
.hdr .upd{font-size:10px;color:var(--or);opacity:.7;margin-top:4px;font-weight:500}
.hdr-r{display:flex;align-items:center;gap:24px}
.bign .n{font-size:44px;font-weight:900;line-height:1;letter-spacing:-1px}
.bign .l{font-size:11px;opacity:.65;font-weight:500;margin-top:2px}
.bdg{border-radius:20px;padding:5px 14px;font-size:12px;font-weight:700;background:rgba(249,91,53,.25);border:1px solid rgba(249,91,53,.5)}
.fbar{background:var(--sf);border-bottom:1px solid var(--bd);padding:10px 32px;position:sticky;top:0;z-index:10;box-shadow:0 1px 4px rgba(0,0,0,.04)}
.fbar-r1{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.fbar-r2{display:flex;gap:14px;align-items:center;flex-wrap:wrap;padding-top:8px;border-top:1px solid var(--bd)}
.fbar label{font-size:10px;font-weight:700;color:var(--t2);text-transform:uppercase;letter-spacing:.6px}
.fbar select,.fbar input[type=date]{border:1.5px solid var(--bd);border-radius:8px;padding:6px 10px;font-size:12px;color:var(--tx);background:var(--bg);outline:none;cursor:pointer;font-family:inherit;transition:border-color .15s}
.fbar select:focus,.fbar input[type=date]:focus{border-color:var(--or)}
.pbt{background:transparent;border:1.5px solid var(--bd);border-radius:20px;padding:5px 13px;font-size:11px;font-weight:600;cursor:pointer;color:var(--t2);transition:all .15s;font-family:inherit}
.pbt.active,.pbt:hover{background:var(--or);color:#fff;border-color:var(--or);box-shadow:0 2px 8px rgba(249,91,53,.3)}
.sep{color:var(--bd);font-size:18px;margin:0 2px}
.main{padding:22px 32px;max-width:1440px;margin:0 auto}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px}
.kpi{background:var(--sf);border-radius:16px;padding:20px 22px;border:1.5px solid var(--bd);text-align:center;transition:box-shadow .2s}
.kpi:hover{box-shadow:0 4px 16px rgba(0,0,0,.07)}
.kpi .lb{font-size:10px;color:var(--t2);text-transform:uppercase;letter-spacing:.7px;margin-bottom:8px;font-weight:600}
.kpi .vl{font-size:28px;font-weight:800;letter-spacing:-.5px}
.kpi .sb{font-size:11px;color:var(--t2);margin-top:5px;font-weight:500}
.dl{display:inline-block;border-radius:10px;padding:3px 9px;font-size:11px;font-weight:700;margin-top:6px}
.dg{background:#DCFCE7;color:#166534}.db{background:#FDEEF6;color:#9B1257}
@media(prefers-color-scheme:dark){.dg{background:#064E3B;color:#6EE7B7}.db{background:#4A0A28;color:#F9A8D4}}
.card{background:var(--sf);border-radius:16px;padding:22px 24px;border:1.5px solid var(--bd);margin-bottom:18px;transition:box-shadow .2s}
.card:hover{box-shadow:0 4px 16px rgba(0,0,0,.07)}
.card h3{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--t2);margin-bottom:16px;border-bottom:1px solid var(--bd);padding-bottom:10px}
.g2{display:grid;grid-template-columns:3fr 2fr;gap:16px;margin-bottom:18px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:18px}
.rrow{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.rn{width:22px;height:22px;border-radius:50%;background:var(--or);color:#fff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;flex-shrink:0}
.rn.b{background:var(--pk)}.rn.c{background:var(--gy)}
.rl{font-size:12px;font-weight:500;line-height:1.35;color:var(--tx)}
.rb{flex:1}.rbb{height:4px;background:var(--bd);border-radius:3px;margin-top:4px}
.rbf{height:4px;background:var(--or);border-radius:3px}
.rc{font-size:14px;font-weight:800;min-width:26px;text-align:right;color:var(--tx)}
.ptl{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--dk);border-bottom:2px solid var(--or);padding-bottom:10px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center}
.ptl span{background:var(--or);color:#fff;border-radius:10px;padding:2px 8px;font-size:10px;font-weight:700}
.igrd{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.ic{background:var(--sf);border-radius:12px;padding:16px 18px;border:1.5px solid var(--bd);border-left:3px solid var(--or);transition:transform .15s}.ic:hover{transform:translateY(-2px)}
.ic.g{border-left-color:#10B981}.ic.r{border-left-color:#EF4444}.ic.y{border-left-color:#F59E0B}.ic.b{border-left-color:#3B82F6}
.ic .ii{font-size:22px;margin-bottom:6px}
.ic .il{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--t2);margin-bottom:5px}
.ic .it{font-size:12px;line-height:1.55;color:var(--tx);font-weight:400}
.empty{text-align:center;padding:32px;color:var(--t2);font-size:13px}
.ftr{text-align:center;padding:20px;font-size:11px;color:var(--t2);font-weight:500;border-top:1px solid var(--bd);margin-top:8px}
@keyframes shake{0%,100%{transform:translateX(0)}25%,75%{transform:translateX(-6px)}50%{transform:translateX(6px)}}
.shk{animation:shake .35s ease}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.g2,.g3{grid-template-columns:1fr}.igrd{grid-template-columns:1fr}.main,.hdr,.fbar{padding-left:16px;padding-right:16px}}
</style>
</head>
<body>
<div class="hdr">
  <div>
    <div class="tag">Coderhouse CX</div>
    <div class="ttl">Dashboard de Devoluciones 2026</div>
    <div class="upd" id="hUpd"></div>
  </div>
  <div class="hdr-r">
    <div class="bign"><div class="n" id="hTot">-</div><div class="l">devoluciones</div></div>
    <div><div class="bdg" id="hCmb">-</div><div style="font-size:10px;opacity:.55;text-align:center;margin-top:5px;font-weight:500" id="hPer"></div></div>
  </div>
</div>
<div class="fbar">
  <div class="fbar-r1">
    <button class="pbt active" data-p="semana">Esta semana</button>
    <button class="pbt" data-p="semana-ant">Sem. anterior</button>
    <button class="pbt" data-p="mes">Este mes</button>
    <button class="pbt" data-p="mes-ant">Mes anterior</button>
    <button class="pbt" data-p="anio">2026 completo</button>
    <span class="sep">|</span>
    <label>Desde</label><input type="date" id="fD">
    <label>Hasta</label><input type="date" id="fH">
  </div>
  <div class="fbar-r2">
    <label>Tipo de baja</label>
    <select id="fT"><option value="">Todos los tipos</option></select>
    <label style="margin-left:8px">Producto</label>
    <select id="fP" style="min-width:200px"><option value="">Todos los productos</option></select>
  </div>
</div>
<div class="main">
  <div class="kpis">
    <div class="kpi"><div class="lb">Total devoluciones</div><div class="vl" id="kTot">-</div><div class="dl" id="kTotD"></div></div>
    <div class="kpi"><div class="lb">Monto ARS devuelto</div><div class="vl" id="kMnt">-</div><div class="dl" id="kMntD"></div></div>
    <div class="kpi"><div class="lb">Promedio diario</div><div class="vl" id="kPrm">-</div><div class="sb">devs / dia</div></div>
    <div class="kpi"><div class="lb">Plataforma 4.0</div><div class="vl" id="kPlt">-</div><div class="sb" id="kPltS"></div></div>
  </div>
  <div class="card"><h3 id="tendTtl">Tendencia</h3><canvas id="cTend" style="max-height:190px"></canvas></div>
  <div class="g2">
    <div class="card" style="margin-bottom:0"><h3>Top motivos de baja</h3><div id="motDiv"></div></div>
    <div class="card" style="margin-bottom:0"><h3>Tipo de baja</h3><canvas id="cTipo" style="max-height:210px"></canvas></div>
  </div>
  <div style="height:18px"></div>
  <div class="g3">
    <div class="card" style="margin-bottom:0" id="pCurso"></div>
    <div class="card" style="margin-bottom:0" id="pCarrera"></div>
    <div class="card" style="margin-bottom:0" id="pDiplo"></div>
  </div>
  <div style="height:18px"></div>
  <div class="card"><h3>Insights del periodo</h3><div class="igrd" id="igrd"></div></div>
</div>
<div class="ftr" id="ftr"></div>
<div id="lov" style="position:fixed;inset:0;z-index:9999;background:linear-gradient(135deg,#F95B35 0%,#22213A 100%);display:flex;align-items:center;justify-content:center">
  <div id="lbx" style="background:#fff;border-radius:24px;padding:44px 52px;text-align:center;width:340px;box-shadow:0 32px 80px rgba(0,0,0,.35)">
    <div style="font-size:38px;margin-bottom:10px">&#128202;</div>
    <div style="font-size:10px;color:#AAA;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;font-weight:600">Coderhouse CX</div>
    <div style="font-size:22px;font-weight:800;color:#22213A;margin-bottom:6px;letter-spacing:-.3px">Devoluciones 2026</div>
    <div style="font-size:12px;color:#AAA;margin-bottom:24px;font-weight:500">Acceso restringido</div>
    <input id="pi" type="password" placeholder="Contraseña de acceso"
      style="width:100%;border:2px solid #EBE3DE;border-radius:12px;padding:13px 15px;font-size:14px;outline:none;margin-bottom:8px;display:block;font-family:inherit;color:#22213A;transition:border-color .15s"
      onfocus="this.style.borderColor='#F95B35'" onblur="this.style.borderColor='#EBE3DE'"
      onkeydown="if(event.key=='Enter')doPwd()">
    <div id="pe" style="color:#EF4444;font-size:12px;min-height:18px;margin-bottom:8px;font-weight:600"></div>
    <button onclick="doPwd()" style="width:100%;background:#F95B35;color:#fff;border:none;border-radius:12px;padding:14px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;transition:opacity .15s" onmouseover="this.style.opacity='.88'" onmouseout="this.style.opacity='1'" id="pbtn">Ingresar</button>
    <div style="font-size:10px;color:#CCC;margin-top:20px;font-weight:500">Solo uso interno &bull; Coderhouse</div>
  </div>
</div>
<script>
""")

parts.append("var DATA=JSON.parse('")
parts.append(DATA_JSON_STR_ESCAPED)
parts.append("""');
var PASS=atob('""" + PASS_B64 + """');
var SK='cdh_dvs_2026';
var cT=null,cTp=null;
(function(){if(sessionStorage.getItem(SK)==='1'){document.getElementById('lov').style.display='none';}})();
function doPwd(){var v=document.getElementById('pi').value,pe=document.getElementById('pe'),pb=document.getElementById('pbtn');if(!v){pe.textContent='Ingresa tu contraseña';return;}pb.textContent='...';pb.disabled=true;pe.textContent='';setTimeout(function(){if(v===PASS){sessionStorage.setItem(SK,'1');document.getElementById('lov').style.display='none';}else{pe.textContent='Contraseña incorrecta';document.getElementById('pi').value='';document.getElementById('lbx').classList.add('shk');setTimeout(function(){document.getElementById('lbx').classList.remove('shk');},400);pb.textContent='Ingresar';pb.disabled=false;document.getElementById('pi').focus();}},300);}
function fmt(n){return '$'+Math.round(n).toLocaleString('es-AR');}function formatM(n){if(n>=1000000)return '$'+(n/1000000).toFixed(1)+'M ARS';if(n>=1000)return '$'+Math.round(n/1000)+'K ARS';return '$'+Math.round(n).toLocaleString('es-AR')+' ARS';}
function pct(a,b){return b>0?((a-b)/b*100):null;}
function pm(v){if(!v)return 0;v=v.replace(/"/g,'').trim();if(v.indexOf(',')>-1)v=v.replace(/\\./g,'').replace(',','.');return parseFloat(v)||0;}
function tods(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function addD(d,n){var r=new Date(d);r.setDate(r.getDate()+n);return r;}
function wkB(r){var d=new Date(r),dy=d.getDay(),diff=dy===0?-6:1-dy,m=new Date(d);m.setDate(d.getDate()+diff);return{from:tods(m),to:tods(addD(m,6))};}
function moB(r){var d=new Date(r);return{from:tods(new Date(d.getFullYear(),d.getMonth(),1)),to:tods(new Date(d.getFullYear(),d.getMonth()+1,0))};}
function prev(from,to){var f=new Date(from+'T12:00:00'),t=new Date(to+'T12:00:00'),days=Math.round((t-f)/86400000)+1;return{from:tods(addD(f,-days)),to:tods(addD(t,-days))};}
function filt(from,to,ti,pr){var prL=pr?pr.toLowerCase():'';return DATA.filter(function(r){return r.f>=from&&r.f<=to&&(!ti||r.t===ti)&&(!prL||(r.d||'').toLowerCase()===prL);});}
function cnt(rows,key,norm){var c={};rows.forEach(function(r){var v=norm?norm(r[key]||''):(r[key]||'');c[v]=(c[v]||0)+1;});return Object.entries(c).sort(function(a,b){return b[1]-a[1];}).filter(function(e){return e[0];});}
function cntNorm(rows,key){var c={},disp={};rows.forEach(function(r){var raw=(r[key]||'').trim(),k=raw.toLowerCase();if(!k)return;c[k]=(c[k]||0)+1;if(!disp[k])disp[k]=raw;});return Object.entries(c).sort(function(a,b){return b[1]-a[1];}).map(function(e){return[disp[e[0]],e[1]];}).filter(function(e){return e[0];});}
function ddays(from,to){return Math.round((new Date(to)-new Date(from))/86400000)+1;}
function gByDay(rows,from,to){var m={},d=new Date(from+'T12:00:00'),t=new Date(to+'T12:00:00');while(d<=t){m[tods(new Date(d))]=0;d.setDate(d.getDate()+1);}rows.forEach(function(r){if(m[r.f]!==undefined)m[r.f]++;});return m;}
function gByWk(rows){var m={};rows.forEach(function(r){var d=new Date(r.f+'T12:00:00'),dy=d.getDay(),diff=dy===0?-6:1-dy,mn=new Date(d);mn.setDate(d.getDate()+diff);var k=tods(mn);m[k]=(m[k]||0)+1;});return m;}
var MES=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
var DIA=['Dom','Lun','Mar','Mie','Jue','Vie','Sab'];
function dlbl(s){var d=new Date(s+'T12:00:00');return DIA[d.getDay()]+' '+d.getDate()+'/'+(d.getMonth()+1);}
function wlbl(s){var d=new Date(s+'T12:00:00');return d.getDate()+' '+MES[d.getMonth()];}
function norm(m){if(!m)return 'Sin especificar';var s=m.toLowerCase();if(/personal|familia|salud/.test(s))return 'Razones personales';if(/tiempo|horario|trabaj|laboral/.test(s))return 'Falta de tiempo';if(/equivoc|error de compra/.test(s))return 'Error en la compra';if(/duplicad|doble cobro/.test(s))return 'Cobro duplicado';if(/interes|cuota/.test(s))return 'Precio / cuotas';if(/disconform|contenido|cursada/.test(s))return 'Disconformidad con el curso';if(/plataforma|sistema|tecnico/.test(s))return 'Problemas de plataforma';if(/escal|chris|gise|deriva/.test(s))return 'Gestion interna';if(/no indica|sin motivo|no especif/.test(s))return 'Sin especificar';if(/viaje|muda/.test(s))return 'Viaje / mudanza';if(/economic|dinero/.test(s))return 'Situacion economica';return m.length>40?m.slice(0,38)+'...':m;}
function delta(id,cur,prv){var el=document.getElementById(id);if(!prv){el.textContent='';return;}var d=pct(cur,prv);if(d===null){el.textContent='';return;}var sube=d>=0;el.className='dl '+(sube?'db':'dg');el.textContent=(sube?'▲':'▼')+' '+Math.abs(d).toFixed(1)+'% vs anterior';}
function render(){var desde=document.getElementById('fD').value,hasta=document.getElementById('fH').value,ti=document.getElementById('fT').value,pr=document.getElementById('fP').value;if(!desde||!hasta)return;var rows=filt(desde,hasta,ti,pr),pv=(window._pvFrom)?{from:window._pvFrom,to:window._pvTo}:prev(desde,hasta),prows=filt(pv.from,pv.to,ti,pr),tot=rows.length,ptot=prows.length;var mnt=rows.reduce(function(s,r){return s+(r.mo==='ARS'?pm(r.mn):0);},0),pmnt=prows.reduce(function(s,r){return s+(r.mo==='ARS'?pm(r.mn):0);},0);var dias=ddays(desde,hasta),prom=(tot/dias).toFixed(1),p40=rows.filter(function(r){return r.pl==='Si';}).length,p40p=tot>0?(p40/tot*100).toFixed(1):0;var now=new Date(),df=new Date(desde+'T12:00:00'),dh=new Date(hasta+'T12:00:00');document.getElementById('hTot').textContent=tot;document.getElementById('hPer').textContent=df.getDate()+' '+MES[df.getMonth()]+' - '+dh.getDate()+' '+MES[dh.getMonth()]+' '+dh.getFullYear();var cm=pct(tot,ptot),cb=document.getElementById('hCmb');if(cm!==null){var su=cm>=0;cb.style.background=su?'rgba(239,68,68,.3)':'rgba(16,185,129,.3)';cb.textContent=(su?'▲':'▼')+' '+Math.abs(cm).toFixed(1)+'% vs anterior ('+ptot+')';}else{cb.textContent='Sin datos anteriores';cb.style.background='rgba(255,255,255,.18)';}document.getElementById('hUpd').textContent='Actualizado: '+now.toLocaleDateString('es-AR')+' '+now.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'});document.getElementById('kTot').textContent=tot;delta('kTotD',tot,ptot);document.getElementById('kMnt').textContent=fmt(mnt);delta('kMntD',mnt,pmnt);document.getElementById('kPrm').textContent=prom;document.getElementById('kPlt').textContent=p40p+'%';document.getElementById('kPltS').textContent=p40+' de '+tot+' en 4.0';document.getElementById('ftr').textContent='Coderhouse CX - Datos al '+now.toLocaleDateString('es-AR');rTend(rows,prows,desde,hasta,pv,dias>45);rTipo(rows);rMot(rows);rProd(rows);rIns(rows,prows,tot,ptot,mnt,pmnt);}
function rTend(rows,prows,desde,hasta,pv,bySem){var byC=bySem?gByWk(rows):gByDay(rows,desde,hasta),byP=bySem?gByWk(prows):gByDay(prows,pv.from,pv.to),labs=Object.keys(byC).sort(),labsP=Object.keys(byP).sort(),lFn=bySem?wlbl:dlbl;document.getElementById('tendTtl').textContent='Tendencia '+(bySem?'semanal':'diaria');if(cT)cT.destroy();cT=new Chart(document.getElementById('cTend'),{type:'bar',data:{labels:labs.map(lFn),datasets:[{label:'Periodo actual',data:labs.map(function(k){return byC[k]||0;}),backgroundColor:'#F95B35',borderRadius:8,order:2},{label:'Periodo anterior',data:labsP.slice(0,labs.length).map(function(k){return byP[k]||0;}),type:'line',borderColor:'#E8197D',backgroundColor:'transparent',borderWidth:2,borderDash:[4,3],borderDashOffset:0,pointRadius:2,tension:.3,order:1}]},options:{plugins:{legend:{position:'top',labels:{boxWidth:10,font:{size:11},color:'#8896A5'}}},scales:{y:{beginAtZero:true,ticks:{precision:0,color:'#8896A5'},grid:{color:'rgba(0,0,0,.04)'}},x:{grid:{display:false},ticks:{font:{size:10},color:'#8896A5'}}}}});}
function rTipo(rows){var tipos=cnt(rows,'t');if(cTp)cTp.destroy();cTp=new Chart(document.getElementById('cTipo'),{type:'doughnut',data:{labels:tipos.map(function(t){return t[0];}),datasets:[{data:tipos.map(function(t){return t[1];}),backgroundColor:['#F95B35','#E8197D','#9CA3AF','#FB8C71','#3A86FF','#06D6A0'],borderWidth:0}]},options:{plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10},color:'#8896A5'}}},cutout:'58%'}});}
function rMot(rows){var ms=cnt(rows,'m',norm).slice(0,8),el=document.getElementById('motDiv');if(!ms.length){el.innerHTML='<div class="empty">Sin datos</div>';return;}var max=ms[0][1],h='';for(var i=0;i<ms.length;i++){var cn=i===0?'rn':i===1?'rn b':'rn c';h+='<div class="rrow"><div class="'+cn+'">'+(i+1)+'</div><div class="rb"><div class="rl">'+ms[i][0]+'</div><div class="rbb"><div class="rbf" style="width:'+(ms[i][1]/max*100).toFixed(0)+'%"></div></div></div><div class="rc">'+ms[i][1]+'</div></div>';}el.innerHTML=h;}
function rProd(rows){var map={curso:{id:'pCurso',lbl:'Cursos'},carrera:{id:'pCarrera',lbl:'Carreras'},diplomatura:{id:'pDiplo',lbl:'Diplomaturas'}};Object.keys(map).forEach(function(tab){var filtered=rows.filter(function(r){return (r.p||'').toLowerCase()===tab;}),ranking=cntNorm(filtered,'d').slice(0,6),max=ranking.length?ranking[0][1]:1;var h='<div class="ptl">'+map[tab].lbl+'<span>'+filtered.length+'</span></div>';if(!ranking.length){h+='<div class="empty">Sin datos</div>';document.getElementById(map[tab].id).innerHTML=h;return;}for(var i=0;i<ranking.length;i++){var cn=i===0?'rn':i===1?'rn b':'rn c';h+='<div class="rrow"><div class="'+cn+'">'+(i+1)+'</div><div class="rb"><div class="rl">'+ranking[i][0]+'</div><div class="rbb"><div class="rbf" style="width:'+(ranking[i][1]/max*100).toFixed(0)+'%"></div></div></div><div class="rc">'+ranking[i][1]+'</div></div>';}document.getElementById(map[tab].id).innerHTML=h;});}
function rIns(rows,prows,tot,ptot,mnt,pmnt){
  var el=document.getElementById('igrd');
  if(tot===0){el.innerHTML='<div class="empty">Sin datos para el período seleccionado</div>';return;}
  var ins=[];

  // ── DÍA PICO ─────────────────────────────────────────────────────────────
  var byDay={},byDayM={};
  rows.forEach(function(r){
    byDay[r.f]=(byDay[r.f]||0)+1;
    if(r.mo==='ARS')byDayM[r.f]=(byDayM[r.f]||0)+pm(r.mn);
  });
  var dkeys=Object.keys(byDay).sort(function(a,b){return byDay[b]-byDay[a];});
  if(dkeys.length){
    var pk=dkeys[0],pkN=byDay[pk],pkM=byDayM[pk]||0;
    var pkD=new Date(pk+'T12:00:00'),pkPct=tot>0?(pkN/tot*100).toFixed(0):0;
    var pkLabel=pkD.getDate()+'/'+('0'+(pkD.getMonth()+1)).slice(-2);
    var pkTxt='El <strong>'+pkLabel+'</strong> registró <strong>'+pkN+' devoluciones</strong>';
    if(pkM>0)pkTxt+=' y <strong>'+formatM(pkM)+'</strong>';
    pkTxt+=' — el máximo del período, concentrando el <strong>'+pkPct+'%</strong> del total.';
    if(dkeys.length>1){var d2=dkeys[1];pkTxt+=' Le sigue el '+new Date(d2+'T12:00:00').getDate()+'/'+(new Date(d2+'T12:00:00').getMonth()+1)+' con '+byDay[d2]+'.';}
    ins.push({icon:'🔴',cls:'r',lbl:pkLabel+' — Día pico',txt:pkTxt});
  }

  // ── EVOLUCIÓN DE TIPO DE BAJA vs período anterior ─────────────────────────
  if(ptot>0&&tot>=3){
    var tC={},tP={};
    rows.forEach(function(r){var t=(r.t||'Sin tipo').trim();tC[t]=(tC[t]||0)+1;});
    prows.forEach(function(r){var t=(r.t||'Sin tipo').trim();tP[t]=(tP[t]||0)+1;});
    var maxSh=null;
    Object.keys(tC).forEach(function(t){
      var pCur=tC[t]/tot*100,pPrv=tP[t]?tP[t]/ptot*100:0,sh=pCur-pPrv;
      if(!maxSh||Math.abs(sh)>Math.abs(maxSh.sh))maxSh={t:t,pCur:pCur,pPrv:pPrv,sh:sh,n:tC[t]};
    });
    if(maxSh&&Math.abs(maxSh.sh)>=3){
      var up=maxSh.sh>0;
      ins.push({icon:up?'📈':'📉',cls:up?'r':'g',
        lbl:(up?'Sube':'Baja')+' en '+maxSh.t,
        txt:'"<strong>'+maxSh.t+'</strong>" representa el <strong>'+maxSh.pCur.toFixed(0)+'%</strong> de las bajas (vs <strong>'+maxSh.pPrv.toFixed(0)+'%</strong> período anterior). Son <strong>'+maxSh.n+' casos</strong>.'
      });
    }
  }

  // ── PRODUCTO / CURSO DOMINANTE ────────────────────────────────────────────
  var topAll=cntNorm(rows,'d');
  if(topAll.length){
    var t1=topAll[0],t1M=0;
    rows.filter(function(r){return (r.d||'').trim().toLowerCase()===t1[0].toLowerCase();})
        .forEach(function(r){if(r.mo==='ARS')t1M+=pm(r.mn);});
    var t1Pct=tot>0?(t1[1]/tot*100).toFixed(0):0;
    var t1Lbl=t1[0].length>32?t1[0].slice(0,30)+'…':t1[0];
    var t1Txt='<strong>'+t1Lbl+'</strong> lidera con <strong>'+t1[1]+' devoluciones</strong>';
    if(t1M>0)t1Txt+=' y <strong>'+formatM(t1M)+'</strong>';
    t1Txt+=', representando el <strong>'+t1Pct+'%</strong> del período.';
    if(topAll[1])t1Txt+=' <strong>'+topAll[1][0]+'</strong> es 2° con '+topAll[1][1]+'.';
    ins.push({icon:'📚',cls:'',lbl:'Producto dominante',txt:t1Txt});
  }

  // ── SEMANA MÁS CARGADA ────────────────────────────────────────────────────
  var byWk={},byWkM={};
  rows.forEach(function(r){
    var d=new Date(r.f+'T12:00:00'),dy=d.getDay(),diff=dy===0?-6:1-dy,mn=new Date(d);
    mn.setDate(d.getDate()+diff);var k=tods(mn);
    byWk[k]=(byWk[k]||0)+1;
    if(r.mo==='ARS')byWkM[k]=(byWkM[k]||0)+pm(r.mn);
  });
  var wkKeys=Object.keys(byWk).sort(function(a,b){return byWk[b]-byWk[a];});
  if(wkKeys.length>=1){
    var w1k=wkKeys[0],w1N=byWk[w1k],w1M=byWkM[w1k]||0;
    var w1D=new Date(w1k+'T12:00:00'),w1E=new Date(w1D);w1E.setDate(w1D.getDate()+6);
    var w1Pct=tot>0?(w1N/tot*100).toFixed(0):0;
    var w1Rng=w1D.getDate()+'/'+(w1D.getMonth()+1)+'-'+w1E.getDate()+'/'+(w1E.getMonth()+1);
    var w1Txt='La semana del <strong>'+w1Rng+'</strong> concentró el <strong>'+w1Pct+'%</strong> del período con <strong>'+w1N+' devoluciones</strong>';
    if(w1M>0)w1Txt+=' y <strong>'+formatM(w1M)+'</strong>';
    w1Txt+='.';
    if(wkKeys.length>1)w1Txt+=' La semana siguiente tuvo '+byWk[wkKeys[1]]+'.';
    ins.push({icon:'📅',cls:'y',lbl:'Semana más cargada',txt:w1Txt});
  }

  // ── PLATAFORMA 4.0 ────────────────────────────────────────────────────────
  var p40=rows.filter(function(r){return r.pl==='Si';}).length;
  if(p40>0){
    var p40p=tot>0?(p40/tot*100).toFixed(0):0;
    var p40pr=ptot>0?prows.filter(function(r){return r.pl==='Si';}).length:0;
    var p40pp=ptot>0?(p40pr/ptot*100).toFixed(0):0;
    var up40=ptot>0&&parseInt(p40p)>parseInt(p40pp);
    var p40Txt='<strong>'+p40p+'%</strong> de las bajas son alumnos en plataforma 4.0 (<strong>'+p40+' casos</strong>).';
    if(ptot>0)p40Txt+=' Período anterior: <strong>'+p40pp+'%</strong> — '+(up40?'la proporción <strong>sube ⚠️</strong>.':'la proporción <strong>baja ✓</strong>.');
    ins.push({icon:'💻',cls:up40?'r':'g',lbl:'Plataforma 4.0',txt:p40Txt});
  }

  // ── TENDENCIA INTERNA: primera vs segunda mitad ───────────────────────────
  if(tot>=8){
    var srtD=Array.from(new Set(rows.map(function(r){return r.f;}))).sort();
    var mid=Math.floor(srtD.length/2);
    if(mid>0){
      var h1=rows.filter(function(r){return r.f<srtD[mid];}),h2=rows.filter(function(r){return r.f>=srtD[mid];});
      var r1=(h1.length/Math.max(1,mid)).toFixed(1),r2=(h2.length/Math.max(1,srtD.length-mid)).toFixed(1);
      var accel=parseFloat(r2)>parseFloat(r1);
      ins.push({icon:accel?'⚠️':'✅',cls:accel?'r':'g',
        lbl:accel?'Ritmo acelerando':'Ritmo bajando',
        txt:'Primera mitad del período: <strong>'+r1+' devs/día</strong>. Segunda mitad: <strong>'+r2+' devs/día</strong>. '+(accel?'El volumen <strong>está subiendo</strong> — monitorear de cerca.':'El volumen <strong>está bajando</strong> — señal positiva.')
      });
    }
  }

  // ── EXTRAS si hay menos de 6 ──────────────────────────────────────────────
  if(ins.length<6){
    // Excepciones
    var exc=rows.filter(function(r){return (r.t||'').toLowerCase().indexOf('excep')>-1;});
    if(exc.length>=2){
      var excC=cntNorm(exc,'d'),excP=tot>0?(exc.length/tot*100).toFixed(0):0;
      var excTxt='<strong>'+exc.length+' excepciones</strong> = <strong>'+excP+'%</strong> del período.';
      if(excC.length)excTxt+=' "<strong>'+excC[0][0]+'</strong>" lidera con '+excC[0][1]+' casos.';
      if(excC[1])excTxt+=' "<strong>'+excC[1][0]+'</strong>": '+excC[1][1]+'.';
      ins.push({icon:'🔥',cls:'r',lbl:'Comisiones bajo presión',txt:excTxt});
    }
  }
  if(ins.length<6){
    // País
    var pa=cnt(rows,'pa');
    if(pa.length>1&&tot>=5){
      var paP=tot>0?(pa[0][1]/tot*100).toFixed(0):0;
      ins.push({icon:'🌎',cls:'b',lbl:'País líder: '+pa[0][0],
        txt:'<strong>'+pa[0][0]+'</strong> concentra el <strong>'+paP+'%</strong> de las bajas (<strong>'+pa[0][1]+'</strong> de '+tot+'). '+
            (pa[1]?'<strong>'+pa[1][0]+'</strong> es 2° con '+pa[1][1]+' casos.':'')
      });
    }
  }
  if(ins.length<6){
    // Motivo top
    var ms=cntNorm(rows,'m').slice(0,1);
    if(ms.length){
      var mPct=tot>0?(ms[0][1]/tot*100).toFixed(0):0;
      ins.push({icon:'🔍',cls:'',lbl:'Motivo principal',
        txt:'"<strong>'+ms[0][0]+'</strong>" es el motivo más frecuente: <strong>'+ms[0][1]+' casos</strong>, el <strong>'+mPct+'%</strong> del total del período.'
      });
    }
  }

  el.innerHTML=ins.slice(0,6).map(function(x){
    return '<div class="ic '+x.cls+'"><div class="ii">'+x.icon+'</div><div class="il">'+x.lbl+'</div><div class="it">'+x.txt+'</div></div>';
  }).join('');
}

function setPreset(p){var t=new Date(),from,to;window._pvFrom=null;window._pvTo=null;if(p==='semana'){var b=wkB(t);from=b.from;to=tods(t);window._pvFrom=tods(addD(new Date(from+'T12:00:00'),-7));window._pvTo=tods(addD(new Date(to+'T12:00:00'),-7));}else if(p==='semana-ant'){var b=wkB(t),pv=prev(b.from,b.to);from=pv.from;to=pv.to;}else if(p==='mes'){var b=moB(t);from=b.from;to=tods(t);var prevMo=moB(new Date(t.getFullYear(),t.getMonth()-1,1));window._pvFrom=prevMo.from;window._pvTo=prevMo.to;}else if(p==='mes-ant'){var d=new Date(t.getFullYear(),t.getMonth()-1,1),b=moB(d);from=b.from;to=b.to;}else if(p==='anio'){from='2026-01-01';to=tods(t);}document.getElementById('fD').value=from;document.getElementById('fH').value=to;render();}
function init(){var tipos=Array.from(new Set(DATA.map(function(r){return r.t;}).filter(Boolean))).sort(),ts=document.getElementById('fT');tipos.forEach(function(t){var o=document.createElement('option');o.value=t;o.textContent=t;ts.appendChild(o);});var seen={},prods=[];DATA.forEach(function(r){var d=(r.d||'').trim(),k=d.toLowerCase();if(k&&!seen[k]){seen[k]=true;prods.push(d);}});prods.sort();var ps=document.getElementById('fP');prods.forEach(function(d){var o=document.createElement('option');o.value=d;o.textContent=d;ps.appendChild(o);});document.querySelectorAll('.pbt').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('.pbt').forEach(function(x){x.classList.remove('active');});b.classList.add('active');setPreset(b.dataset.p);});});['fD','fH'].forEach(function(id){document.getElementById(id).addEventListener('change',function(){document.querySelectorAll('.pbt').forEach(function(x){x.classList.remove('active');});window._pvFrom=null;window._pvTo=null;render();});});document.getElementById('fT').addEventListener('change',render);document.getElementById('fP').addEventListener('change',render);rMensual();setPreset('semana');}
init();
</script>
</body>
</html>""")

HTML = ''.join(parts)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)
print(f"index.html generado: {len(HTML):,} chars en {out_path}")
