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
from xml.sax.saxutils import escape


# =========================
# DATOS EMPRESA
# =========================
EMPRESA = {
    "nombre": "Punihard",
    "direccion": "",
    "telefono": "",
    "email": "",
    "cuit": "",
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
        bottomMargin=2 * cm,
    )
    story = []
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "title",
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1a1a2e"),
    )
    story.append(Paragraph(EMPRESA["nombre"], title))
    if EMPRESA["direccion"]:
        story.append(Paragraph(escape(EMPRESA["direccion"]), styles["Normal"]))
    if EMPRESA["telefono"]:
        story.append(Paragraph(f"Tel: {escape(EMPRESA['telefono'])}", styles["Normal"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"REMITO N° {remito.numero}", title))
    story.append(Spacer(1, 0.5 * cm))

    venta = remito.venta
    cliente = venta.cliente if venta and venta.cliente_id else None
    cliente_nombre = remito.destinatario or (
        cliente.nombre_completo if cliente else "Entrega independiente"
    )
    info = [
        ["Destinatario", cliente_nombre],
        ["Fecha", remito.fecha.strftime("%d/%m/%Y %H:%M")],
        ["Dirección", remito.direccion_entrega or "—"],
        ["Venta N°", venta.numero if venta else "Independiente"],
        ["Estado", remito.estado],
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

    data = [["Artículo / descripción", "Cantidad", "Unidad"]]
    for detail in remito.detalles:
        data.append([
            escape(detail.descripcion),
            f"{detail.cantidad:g}",
            escape(detail.unidad),
        ])
    table2 = Table(data, colWidths=[10 * cm, 3 * cm, 4 * cm], repeatRows=1)
    table2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))
    story.append(table2)
    story.append(Spacer(1, 0.5 * cm))
    if remito.observaciones:
        story.append(Paragraph(f"Observaciones: {escape(remito.observaciones)}", styles["Normal"]))
    story.extend([
        Spacer(1, 1 * cm),
        Paragraph("Firma y aclaración: ____________________________________", styles["Normal"]),
    ])
    doc.build(story)
    buffer.seek(0)
    return buffer


def generar_ticket_pdf(venta):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ticket_title",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#ff7b00"),
    )
    story = [
        Paragraph("PUNIHARD", title),
        Paragraph("Comprobante interno — no válido como factura", styles["Normal"]),
        Spacer(1, 0.4 * cm),
        Paragraph(f"Venta: {venta.numero}", styles["Normal"]),
        Paragraph(f"Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}", styles["Normal"]),
        Paragraph(
            f"Cliente: {escape(venta.cliente.nombre_completo if venta.cliente else 'Consumidor Final')}",
            styles["Normal"],
        ),
        Paragraph(f"Pago: {venta.metodo_pago}", styles["Normal"]),
        Spacer(1, 0.3 * cm),
    ]
    rows = [["Artículo", "Cant.", "P. unitario", "Subtotal"]]
    for detail in venta.detalles:
        rows.append([
            escape(detail.articulo.nombre),
            f"{detail.cantidad:g}",
            f"${detail.precio_unitario:,.2f}",
            f"${detail.subtotal:,.2f}",
        ])
    table = Table(rows, colWidths=[8 * cm, 2 * cm, 3 * cm, 3 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([
        table,
        Spacer(1, 0.4 * cm),
        Paragraph(f"Subtotal: ${venta.total:,.2f}", styles["Normal"]),
        Paragraph(f"Descuento: ${venta.descuento:,.2f}", styles["Normal"]),
        Paragraph(f"<b>TOTAL: ${venta.total_final:,.2f}</b>", styles["Heading2"]),
    ])
    if venta.metodo_pago == "Efectivo":
        story.append(Paragraph(f"Recibido: ${venta.importe_recibido:,.2f}", styles["Normal"]))
        story.append(Paragraph(
            f"Vuelto: ${max(venta.importe_recibido - venta.total_final, 0):,.2f}",
            styles["Normal"],
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
        cliente = v.cliente.nombre_completo if v.cliente else "CF"

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