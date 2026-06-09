from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datos en memoria
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
    telefono: str
    servicio: str
    motivo: str

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
    return {"citas_hoy": len(citas_hoy), "total": len(citas)}

# HTML SIMPLE
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
        .tab { flex: 1; padding: 10px; background: #ddd; text-align: center; cursor: pointer; border-radius: 5px; }
        .tab.active { background: #2E7D32; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #2E7D32; margin-bottom: 15px; }
        input, select, textarea { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #2E7D32; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button.danger { background: #C62828; width: auto; padding: 5px 10px; }
        .servicio-item { display: flex; justify-content: space-between; padding: 10px; background: #f9f9f9; margin-bottom: 5px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #A8E6CF; }
        .numero { font-size: 36px; color: #2E7D32; text-align: center; }
    </style>
</head>
<body>
<div class="container">
    <h1>📋 AutoAgenda</h1>
    <div class="sub">"Configura una vez. Agenda siempre"</div>
    
    <div class="tabs">
        <div class="tab active" onclick="mostrar('servicios')">Servicios</div>
        <div class="tab" onclick="mostrar('agendar')">Agendar</div>
        <div class="tab" onclick="mostrar('citas')">Citas</div>
        <div class="tab" onclick="mostrar('resumen')">Resumen</div>
    </div>
    
    <div id="servicios-tab" class="tab-content active">
        <div class="card">
            <h2>Agregar Servicio</h2>
            <input type="text" id="nuevoServicio" placeholder="Nombre">
            <button onclick="agregarServicio()">Agregar</button>
        </div>
        <div class="card">
            <h2>Mis Servicios</h2>
            <div id="listaServicios"></div>
        </div>
    </div>
    
    <div id="agendar-tab" class="tab-content">
        <div class="card">
            <h2>Nueva Cita</h2>
            <input type="date" id="fecha">
            <input type="time" id="hora">
            <input type="text" id="nombre" placeholder="Cliente">
            <input type="text" id="telefono" placeholder="Teléfono">
            <select id="servicioSelect"></select>
            <textarea id="motivo" placeholder="Motivo" rows="2"></textarea>
            <button onclick="agendar()">Agendar</button>
        </div>
    </div>
    
    <div id="citas-tab" class="tab-content">
        <div class="card">
            <h2>Citas</h2>
            <input type="date" id="filtroFecha" onchange="cargarCitas()">
            <div id="listaCitas"></div>
        </div>
    </div>
    
    <div id="resumen-tab" class="tab-content">
        <div class="card">
            <h2>Resumen</h2>
            <div class="numero" id="totalHoy">0</div>
            <p>Citas para hoy</p>
        </div>
        <div class="card">
            <h2>Todas las Citas</h2>
            <div id="todasCitas"></div>
        </div>
    </div>
</div>

<script>
    function mostrar(tab) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(tab + '-tab').classList.add('active');
        event.target.classList.add('active');
        if (tab === 'servicios') cargarServicios();
        if (tab === 'citas') cargarCitas();
        if (tab === 'resumen') cargarResumen();
    }
    
    async function cargarServicios() {
        const res = await fetch('/api/servicios');
        const servicios = await res.json();
        const select = document.getElementById('servicioSelect');
        select.innerHTML = servicios.map(s => `<option value="${s.nombre}">${s.nombre}</option>`).join('');
        
        document.getElementById('listaServicios').innerHTML = servicios.map(s => `
            <div class="servicio-item">
                <span>📌 ${s.nombre}</span>
                <button class="danger" onclick="eliminarServicio(${s.id})">Eliminar</button>
            </div>
        `).join('');
    }
    
    async function agregarServicio() {
        const nombre = document.getElementById('nuevoServicio').value.trim();
        if (!nombre) return;
        await fetch('/api/servicios', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nombre})
        });
        document.getElementById('nuevoServicio').value = '';
        cargarServicios();
    }
    
    async function eliminarServicio(id) {
        if (confirm('¿Eliminar?')) {
            await fetch(`/api/servicios/${id}`, {method: 'DELETE'});
            cargarServicios();
        }
    }
    
    async function cargarCitas() {
        const fecha = document.getElementById('filtroFecha').value || new Date().toISOString().split('T')[0];
        document.getElementById('filtroFecha').value = fecha;
        const res = await fetch(`/api/citas?fecha=${fecha}`);
        const citas = await res.json();
        const container = document.getElementById('listaCitas');
        if (citas.length === 0) {
            container.innerHTML = '<p>No hay citas</p>';
        } else {
            container.innerHTML = `
                <table>
                    <tr><th>Hora</th><th>Cliente</th><th>Servicio</th><th></th></tr>
                    ${citas.map(c => `
                        <tr>
                            <td>${c.hora}</td>
                            <td>${c.nombre}</td>
                            <td>${c.servicio}</td>
                            <td><button class="danger" onclick="eliminarCita(${c.id})">X</button></td>
                        </tr>
                    `).join('')}
                </table>
            `;
        }
    }
    
    async function eliminarCita(id) {
        if (confirm('¿Cancelar cita?')) {
            await fetch(`/api/citas/${id}`, {method: 'DELETE'});
            cargarCitas();
            cargarResumen();
        }
    }
    
    async function agendar() {
        const fecha = document.getElementById('fecha').value;
        const hora = document.getElementById('hora').value;
        const nombre = document.getElementById('nombre').value.trim();
        const telefono = document.getElementById('telefono').value;
        const servicio = document.getElementById('servicioSelect').value;
        const motivo = document.getElementById('motivo').value;
        
        if (!fecha || !hora || !nombre) {
            alert('Complete fecha, hora y nombre');
            return;
        }
        
        const res = await fetch('/api/citas', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({fecha, hora, nombre, telefono, servicio, motivo})
        });
        
        if (res.ok) {
            document.getElementById('nombre').value = '';
            document.getElementById('telefono').value = '';
            document.getElementById('motivo').value = '';
            alert('Cita agendada');
            cargarCitas();
            cargarResumen();
        } else {
            alert('Error');
        }
    }
    
    async function cargarResumen() {
        const res = await fetch('/api/resumen');
        const data = await res.json();
        document.getElementById('totalHoy').innerText = data.citas_hoy;
        
        const resTodas = await fetch('/api/citas');
        const todas = await resTodas.json();
        const container = document.getElementById('todasCitas');
        if (todas.length === 0) {
            container.innerHTML = '<p>No hay citas</p>';
        } else {
            container.innerHTML = `
                <table>
                    <tr><th>Fecha</th><th>Hora</th><th>Cliente</th><th>Servicio</th></tr>
                    ${todas.map(c => `
                        <tr>
                            <td>${c.fecha}</td>
                            <td>${c.hora}</td>
                            <td>${c.nombre}</td>
                            <td>${c.servicio}</td>
                        </tr>
                    `).join('')}
                </table>
            `;
        }
    }
    
    // Inicializar
    cargarServicios();
    document.getElementById('filtroFecha').value = new Date().toISOString().split('T')[0];
    document.getElementById('fecha').value = new Date().toISOString().split('T')[0];
</script>
</body>
</html>
"""

@app.get("/")
def root():
    return HTMLResponse(HTML)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
