from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime


# =========================
# DATOS EMPRESA
# =========================
EMPRESA = {
    "nombre": "Ferretería El Tornillo",
    "direccion": "Av. Principal 1234",
    "telefono": "(011) 4567-8900",
    "email": "info@ferreteria.com",
    "cuit": "20-12345678-9",
}


# =========================
# REMITO PDF
# =========================
def generar_remito_pdf(remito):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    story = []
    styles = getSampleStyleSheet()

    # =========================
    # HEADER
    # =========================
    title = ParagraphStyle(
        "title",
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1a1a2e")
    )

    story.append(Paragraph(EMPRESA["nombre"], title))
    story.append(Paragraph(EMPRESA["direccion"], styles["Normal"]))
    story.append(Paragraph(f"Tel: {EMPRESA['telefono']}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(HRFlowable(width="100%", thickness=2))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(f"REMITO N° {remito.numero}", title))
    story.append(Spacer(1, 0.5 * cm))

    venta = remito.venta_rel
    cliente = venta.cliente_rel if venta.cliente_id else None

    cliente_nombre = cliente.nombre_completo if cliente else "Consumidor Final"

    # =========================
    # INFO CLIENTE
    # =========================
    info = [
        ["Cliente", cliente_nombre],
        ["Fecha", remito.fecha.strftime("%d/%m/%Y %H:%M")],
        ["Venta N°", venta.numero],
    ]

    table = Table(info, colWidths=[4 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    # =========================
    # DETALLE PRODUCTOS
    # =========================
    data = [["Producto", "Cant", "Precio", "Subtotal"]]

    for d in venta.detalles:
        data.append([
            d.articulo.nombre,
            str(d.cantidad),
            f"{d.precio_unitario:.2f}",
            f"{d.subtotal:.2f}"
        ])

    table2 = Table(data, colWidths=[8 * cm, 2 * cm, 3 * cm, 3 * cm])

    table2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))

    story.append(table2)
    story.append(Spacer(1, 0.5 * cm))

    # =========================
    # TOTALES
    # =========================
    total = [
        ["Subtotal", f"{venta.total:.2f}"],
        ["Descuento", f"{venta.descuento}%"],
        ["TOTAL", f"{venta.total_final:.2f}"],
    ]

    table3 = Table(total, colWidths=[5 * cm, 5 * cm])

    table3.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    story.append(table3)
    story.append(Spacer(1, 1 * cm))

    story.append(Paragraph(
        "Documento no válido como factura",
        styles["Normal"]
    ))

    doc.build(story)
    buffer.seek(0)

    return buffer


# =========================
# REPORTE VENTAS PDF
# =========================
def generar_reporte_ventas_pdf(ventas, titulo):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []

    style = ParagraphStyle(
        "h",
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1a1a2e")
    )

    story.append(Paragraph(titulo, style))
    story.append(Spacer(1, 0.5 * cm))

    data = [["N°", "Fecha", "Cliente", "Total"]]

    total_general = 0

    for v in ventas:
        cliente = v.cliente_rel.nombre_completo if v.cliente_id else "CF"

        data.append([
            v.numero,
            v.fecha.strftime("%d/%m/%Y"),
            cliente,
            f"{v.total_final:.2f}"
        ])

        total_general += v.total_final

    data.append(["", "", "TOTAL", f"{total_general:.2f}"])

    table = Table(data, colWidths=[3 * cm, 4 * cm, 6 * cm, 4 * cm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))

    story.append(table)

    doc.build(story)
    buffer.seek(0)

    return buffer