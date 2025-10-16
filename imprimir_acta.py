import os
from datetime import datetime
from docxtpl import DocxTemplate
import modelo

# Rutas relativas al directorio del script
BASE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(BASE, "plantillas", "acta_garantia.docx")
OUT = os.path.join(BASE, "docs")

from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from docxtpl import DocxTemplate
import modelo

BASE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(BASE, "plantillas", "acta_garantia.docx")
OUT = os.path.join(BASE, "docs")

def generar_acta_para_placa(placa: str, creado_por: str = None, obs: str = None):
    """
    Genera un acta de garantía en formato DOCX (y opcionalmente PDF) 
    para un vehículo específico, consultando datos desde la base de datos.
    
    Args:
        placa: Placa del vehículo
        creado_por: Usuario que genera el acta (opcional)
        obs: Observaciones adicionales (opcional)
        
    Returns:
        tupla: (acta_id, ruta_docx, ruta_pdf)
    """
    # Consultar datos del vehículo y propietario
    r = modelo.obtener_datos_acta(placa)
    if not r:
        raise ValueError(f"Vehículo con placa {placa} no encontrado")
    
    placa, fe, fs, nom, ape, ced, tel, dirc, marca, motor = r

    # Calcular fecha de elaboración (hoy) y vigencia (3 años después)
    fecha_elaboracion = datetime.now()
    fecha_vigencia = fecha_elaboracion + relativedelta(years=3)

    # Construir contexto para la plantilla
    ctx = {
        "vehiculo_placa": placa,
        "fecha_entrada": fe or "",
        "fecha_salida": fs or "",
        "fecha_elaboracion": fecha_elaboracion.strftime("%d/%m/%Y"),
        "vigencia_garantia": fecha_vigencia.strftime("%d/%m/%Y"),
        "cliente_nombre": f"{nom or ''} {ape or ''}".strip(),
        "cliente_cedula": ced or "",
        "cliente_telefono": tel or "",
        "cliente_direccion": dirc or "",
        "vehiculo_marca": marca or "",
        "vehiculo_motor": motor or "",
        "empresa_nombre": "LABORATORIO SUR DIESEL PITALITO",
        "empresa_nit": "1083925113-7",
        "empresa_direccion": "Calle 4 #14-52, Villa Matilde",
        "representante": "CARLOS ALBERTO MENDOZA MEDINA"
    }

    # Crear directorio de salida si no existe
    os.makedirs(OUT, exist_ok=True)
    
    # Generar nombre único con timestamp
    nombre = f"Acta_{placa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    docx_path = os.path.join(OUT, nombre)

    # Renderizar plantilla DOCX
    doc = DocxTemplate(TPL)
    doc.render(ctx)
    doc.save(docx_path)

    # Convertir a PDF (opcional, requiere Word en Windows)
    pdf_path = None
    try:
        from docx2pdf import convert
        pdf_path = docx_path.replace(".docx", ".pdf")
        convert(docx_path, pdf_path)
    except Exception:
        # Conversión a PDF opcional - no detiene el proceso si falla
        pdf_path = None

    # Registrar acta en base de datos
    acta_id = modelo.crear_acta_garantia(
        placa=placa,
        fecha_elaboracion=fecha_elaboracion.strftime("%Y-%m-%d"),
        ruta_docx=docx_path,
        ruta_pdf=pdf_path,
        obs=obs,
        creado_por=creado_por
    )
    
    return acta_id, docx_path, pdf_path
