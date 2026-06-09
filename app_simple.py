from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

servicios = [
    {"id": 1, "nombre": "Consulta General"},
    {"id": 2, "nombre": "Seguimiento"},
    {"id": 3, "nombre": "Urgencia"}
]
citas = []
contador = 4

class ServicioInput(BaseModel):
    nombre: str

class CitaInput(BaseModel):
    fecha: str
    hora: str
    nombre: str
    telefono: str = ""
    servicio: str
    motivo: str = ""

@app.get("/api/servicios")
def get_servicios():
    return servicios

@app.post("/api/servicios")
def add_servicio(data: ServicioInput):
    global contador
    nuevo = {"id": contador, "nombre": data.nombre}
    servicios.append(nuevo)
    contador += 1
    return {"success": True}

@app.delete("/api/servicios/{id}")
def delete_servicio(id: int):
    global servicios
    servicios = [s for s in servicios if s["id"] != id]
    return {"success": True}

@app.get("/api/citas")
def get_citas(fecha: Optional[str] = None):
    if fecha:
        return [c for c in citas if c["fecha"] == fecha]
    return citas

@app.post("/api/citas")
def add_cita(data: CitaInput):
    nueva = {
        "id": len(citas) + 1,
        "fecha": data.fecha,
        "hora": data.hora,
        "nombre": data.nombre,
        "telefono": data.telefono,
        "servicio": data.servicio,
        "motivo": data.motivo
    }
    citas.append(nueva)
    return {"success": True}

@app.delete("/api/citas/{id}")
def delete_cita(id: int):
    global citas
    citas = [c for c in citas if c["id"] != id]
    return {"success": True}

@app.get("/api/resumen")
def get_resumen():
    hoy = datetime.now().strftime("%Y-%m-%d")
    citas_hoy = [c for c in citas if c["fecha"] == hoy]
    return {"citas_hoy": len(citas_hoy), "total_citas": len(citas)}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoAgenda</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #f0f2f5; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #2E7D32; text-align: center; }
        .sub { text-align: center; color: #666; margin-bottom: 20px; }
        .tabs { display: flex; gap: 5px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { flex: 1; padding: 10px; background: #ddd; text-align: center; cursor: pointer; border-radius: 5px; font-weight: bold; }
        .tab.active { background: #2E7D32; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { color: #2E7D32; margin-bottom: 15px; font-size: 18px; border-left: 4px solid #A8E6CF; padding-left: 10px; }
        input, select, textarea { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #2E7D32; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button.danger { background: #C62828; width: auto; padding: 5px 10px; }
        .servicio-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #f9f9f9; margin-bottom: 5px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #A8E6CF; color: #2E7D32; }
        .numero-grande { font-size: 48px; color: #2E7D32; text-align: center; font-weight: bold; }
        .text-center { text-align: center; }
        .horario-sugerido { background: #e8f5e9; padding: 8px 12px; margin: 3px; border-radius: 5px; cursor: pointer; display: inline-block; }
    </style>
</head>
<body>
<div class="container">
    <h1>📋 AutoAgenda</h1>
    <div class="sub">"Configura una vez. Agenda siempre"</div>
    
    <div class="tabs">
        <div class="tab active" onclick="mostrarTab('servicios')">Servicios</div>
        <div class="tab" onclick="mostrarTab('agendar')">Agendar</div>
        <div class="tab" onclick="mostrarTab('citas')">Citas</div>
        <div class="tab" onclick="mostrarTab('resumen')">Resumen</div>
    </div>
    
    <div id="tab-servicios" class="tab-content active">
        <div class="card">
            <h2>➕ Agregar Servicio</h2>
            <input type="text" id="nuevoServicio" placeholder="Nombre del servicio">
            <button onclick="agregarServicio()">Agregar</button>
        </div>
        <div class="card">
            <h2>📋 Mis Servicios</h2>
            <div id="listaServicios"></div>
        </div>
    </div>
    
    <div id="tab-agendar" class="tab-content">
        <div class="card">
            <h2>➕ Nueva Cita</h2>
            <input type="date" id="citaFecha">
            <input type="time" id="citaHora">
            <input type="text" id="citaNombre" placeholder="Nombre del cliente">
            <input type="text" id="citaTelefono" placeholder="Teléfono">
            <select id="citaServicio"></select>
            <textarea id="citaMotivo" placeholder="Motivo" rows="2"></textarea>
            <button onclick="agendarCita()">Agendar Cita</button>
        </div>
    </div>
    
    <div id="tab-citas" class="tab-content">
        <div class="card">
            <h2>📅 Citas por Fecha</h2>
            <input type="date" id="filtroFecha" onchange="cargarCitas()">
            <div id="listaCitas"></div>
        </div>
    </div>
    
    <div id="tab-resumen" class="tab-content">
        <div class="card">
            <h2>📊 Resumen del Día</h2>
            <div class="numero-grande" id="totalHoy">0</div>
            <p class="text-center">Citas para hoy</p>
        </div>
        <div class="card">
            <h2>📋 Todas las Citas</h2>
            <div id="todasCitas"></div>
        </div>
    </div>
</div>

<script>
    function mostrarTab(tab) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(`tab-${tab}`).classList.add('active');
        event.target.classList.add('active');
        if (tab === 'servicios') cargarServicios();
        if (tab === 'citas') cargarCitas();
        if (tab === 'resumen') cargarResumen();
        if (tab === 'agendar') cargarServiciosSelect();
    }
    
    async function cargarServicios() {
        const res = await fetch('/api/servicios');
        const servicios = await res.json();
        const container = document.getElementById('listaServicios');
        if (servicios.length === 0) {
            container.innerHTML = '<p>No hay servicios</p>';
        } else {
            container.innerHTML = servicios.map(s => `
                <div class="servicio-item">
                    <span>📌 ${s.nombre}</span>
                    <button class="danger" onclick="eliminarServicio(${s.id})">Eliminar</button>
                </div>
            `).join('');
        }
    }
    
    async function cargarServiciosSelect() {
        const res = await fetch('/api/servicios');
        const servicios = await res.json();
        const select = document.getElementById('citaServicio');
        select.innerHTML = servicios.map(s => `<option value="${s.nombre}">${s.nombre}</option>`).join('');
    }
    
    async function agregarServicio() {
        const nombre = document.getElementById('nuevoServicio').value.trim();
        if (!nombre) { alert('Escribe un nombre'); return; }
        const res = await fetch('/api/servicios', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nombre})
        });
        if (res.ok) {
            document.getElementById('nuevoServicio').value = '';
            cargarServicios();
            cargarServiciosSelect();
            alert('Servicio agregado');
        } else {
            alert('Error');
        }
    }
    
    async function eliminarServicio(id) {
        if (confirm('¿Eliminar este servicio?')) {
            await fetch(`/api/servicios/${id}`, {method: 'DELETE'});
            cargarServicios();
            cargarServiciosSelect();
        }
    }
    
    async function cargarCitas() {
        const fecha = document.getElementById('filtroFecha').value || new Date().toISOString().split('T')[0];
        document.getElementById('filtroFecha').value = fecha;
        const res = await fetch(`/api/citas?fecha=${fecha}`);
        const citas = await res.json();
        const container = document.getElementById('listaCitas');
        if (citas.length === 0) {
            container.innerHTML = '<p>No hay citas para esta fecha</p>';
        } else {
            container.innerHTML = `
                <table>
                    <thead><tr><th>Hora</th><th>Cliente</th><th>Servicio</th><th></th></tr></thead>
                    <tbody>
                        ${citas.map(c => `
                            <tr>
                                <td>${c.hora}</td>
                                <td>${c.nombre}</td>
                                <td>${c.servicio}</td>
                                <td><button class="danger" onclick="eliminarCita(${c.id})">X</button></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    }
    
    async function eliminarCita(id) {
        if (confirm('¿Cancelar esta cita?')) {
            await fetch(`/api/citas/${id}`, {method: 'DELETE'});
            cargarCitas();
            cargarResumen();
        }
    }
    
    async function agendarCita() {
        const fecha = document.getElementById('citaFecha').value;
        const hora = document.getElementById('citaHora').value;
        const nombre = document.getElementById('citaNombre').value.trim();
        const telefono = document.getElementById('citaTelefono').value;
        const servicio = document.getElementById('citaServicio').value;
        const motivo = document.getElementById('citaMotivo').value;
        
        if (!fecha) { alert('Selecciona fecha'); return; }
        if (!hora) { alert('Selecciona hora'); return; }
        if (!nombre) { alert('Escribe nombre'); return; }
        
        const res = await fetch('/api/citas', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({fecha, hora, nombre, telefono, servicio, motivo})
        });
        
        if (res.ok) {
            document.getElementById('citaNombre').value = '';
            document.getElementById('citaTelefono').value = '';
            document.getElementById('citaMotivo').value = '';
            alert('Cita agendada');
            cargarCitas();
            cargarResumen();
        } else {
            alert('Error');
        }
    }
    
    async function cargarResumen() {
        const hoy = new Date().toISOString().split('T')[0];
        const res = await fetch(`/api/citas?fecha=${hoy}`);
        const citasHoy = await res.json();
        document.getElementById('totalHoy').innerText = citasHoy.length;
        
        const resTodas = await fetch('/api/citas');
        const todas = await resTodas.json();
        const container = document.getElementById('todasCitas');
        if (todas.length === 0) {
            container.innerHTML = '<p>No hay citas agendadas</p>';
        } else {
            container.innerHTML = `
                <table>
                    <thead><tr><th>Fecha</th><th>Hora</th><th>Cliente</th><th>Servicio</th></tr></thead>
                    <tbody>
                        ${todas.map(c => `
                            <tr>
                                <td>${c.fecha}</td>
                                <td>${c.hora}</td>
                                <td>${c.nombre}</td>
                                <td>${c.servicio}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    }
    
    // Inicializar
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('citaFecha').value = hoy;
    document.getElementById('filtroFecha').value = hoy;
    cargarServicios();
    cargarServiciosSelect();
</script>
</body>
</html>
"""

@app.get("/")
def root():
    return HTMLResponse(HTML)

if __name__ == "__main__":
    import uvicorn
    print("\n=== AutoAgenda iniciada ===")
    print("Abre: http://localhost:8000")
    print("==========================\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
