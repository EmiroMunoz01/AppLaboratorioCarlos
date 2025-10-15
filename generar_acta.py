import os
from datetime import datetime
from docxtpl import DocxTemplate
import modelo

BASE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(BASE, "plantillas", "acta_garantia.docx")
OUT = os.path.join(BASE, "docs")


def generar_acta_para_placa(placa: str, creado_por: str = None, obs: str = None):
    r = modelo.obtener_datos_acta(placa)
    if not r:
        raise ValueError("Vehículo no encontrado")
    placa, fe, fs, nom, ape, ced, tel, dirc, marca, motor = r

    ctx = {
        "vehiculo_placa": placa,
        "fecha_entrada": fe or "",
        "fecha_salida": fs or "",
        "fecha_elaboracion": datetime.now().strftime("%d/%m/%Y"),
        "cliente_nombre": f"{nom or ''} {ape or ''}".strip(),
        "cliente_cedula": ced or "",
        "cliente_telefono": tel or "",
        "cliente_direccion": dirc or "",
        "vehiculo_marca": marca or "",
        "vehiculo_motor": motor or "",
        "empresa_nombre": "LABORATORIO SUR DIESEL PITALITO",
        "empresa_nit": "1083925113-7",
        "empresa_direccion": "Calle 4 #14-52, Villa Matilde",
    }

    os.makedirs(OUT, exist_ok=True)
    nombre = f"Acta_{placa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    docx_path = os.path.join(OUT, nombre)

    doc = DocxTemplate(TPL)
    doc.render(ctx)
    doc.save(docx_path)

    # PDF opcional si tienes Word (Windows)
    pdf_path = None
    try:
        from docx2pdf import convert

        pdf_path = docx_path.replace(".docx", ".pdf")
        convert(docx_path, pdf_path)
    except Exception:
        pdf_path = None

    acta_id = modelo.crear_acta_garantia(
        placa=placa,
        fecha_elaboracion=datetime.now().strftime("%Y-%m-%d"),
        ruta_docx=docx_path,
        ruta_pdf=pdf_path,
        obs=obs,
        creado_por=creado_por,
    )
    return acta_id, docx_path, pdf_path
