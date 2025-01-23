import PyPDF2
import re
from datetime import datetime

def pdf_to_ent(pdf_path, ent_path):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            content = ""

            for page in reader.pages:
                content += page.extract_text() + "\n"

        ent_content = ""

        factura = re.search(r"Invoice\s+INV/([\d/]+)", content)
        rif = re.search(r"Tax ID[:\s]*([JVEG]-\d+)", content)
        cliente = re.search(r"La Mansión de Víctor", content)
        direccion = re.search(r"La Mansión de Víctor\s+(.*?)\s+Venezuela", content, re.DOTALL)
        fecha = re.search(r"Invoice Date[:\s]*([\d/]+)", content)

        ent_content += f"FACTURA:         {factura.group(1).replace('/', '') if factura else '000000001'}\n"
        ent_content += f"RIF:             {rif.group(1) if rif else 'J000000000'}\n"
        ent_content += f"CLIENTE:         {cliente.group(0) if cliente else 'CLIENTE GENERICO'}\n"
        ent_content += f"DIRECCION1:      {direccion.group(1).strip().replace('\n', ' ') if direccion else 'DIRECCION DESCONOCIDA'}\n"

        if fecha:
            # Convertir la fecha de MM/DD/AAAA a MM-DD-AAAA
            fecha_obj = datetime.strptime(fecha.group(1), "%m/%d/%Y")
            fecha_formateada = fecha_obj.strftime("%m-%d-%Y")
        else:
            fecha_formateada = '01-01-2000'

        ent_content += f"FECHA:           {fecha_formateada}\n"
        ent_content += f"DESCRIPCION.......................................    COD.................... .....CANT  ..IVA  PRECIO\n"

        product_pattern = r"\[(\S+)\]\s+(.+?)\s+([\d\.]+)\s+Units\s+([\d\.]+)\s+\$\s+([\d\.]+)"
        products = re.findall(product_pattern, content)

        subtotal = 0
        for product in products:
            code, description, quantity, unit_price, total_price = product
            subtotal += float(total_price)
            ent_content += f"{description[:40]:<40} {code:<20} {quantity:<10} ---   {total_price:<10}\n"

        ent_content += f"SUB-TOTAL:           {subtotal:.2f}\n"
        ent_content += f"DESCUENTO:           0.00\n"
        ent_content += f"TOTAL A PAGAR:       {subtotal:.2f}\n"
        ent_content += f"EFECTIVO:            {subtotal:.2f}\n"
        ent_content += f"CHEQUES:             0.00\n"
        ent_content += f"TARJ/DÉBITO:         0.00\n"
        ent_content += f"TARJ/CRÉDITO:        0.00\n"
        ent_content += f"PAGO MÓVIL:          0.00\n"
        ent_content += f"NOTA:           CUALQUIER NOTA QUE NECESITES IMPRIMIR\n" * 4

        with open(ent_path, 'w', encoding='utf-8') as ent_file:
            ent_file.write(ent_content)

        print(f"Archivo .ent generado con éxito: {ent_path}")

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

# Ruta del archivo PDF de entrada y del archivo .ent de salida
pdf_path = "INV_2025_00010.pdf"  # Cambia a la ruta real del archivo
ent_path = "fa000000013.ent"  # Nombre del archivo de salida

# Ejecutar la función
pdf_to_ent(pdf_path, ent_path)
