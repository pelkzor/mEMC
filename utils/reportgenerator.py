import json
from datetime import datetime
import os
import matplotlib.pyplot as plt
import tempfile
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

def json_to_pdf(json_path: Path, pdf_path: Path, figure=None):
    with open(json_path, "r") as f:
        data = json.load(f)

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4

    time_str = data.get('time', 'N/A')
    if time_str != 'N/A':
        try:
            dt = datetime.strptime(time_str, "%d%m%y%H%M")
            formatted_time = dt.strftime("%d-%m-%y %H:%M")
        except ValueError:
            formatted_time = time_str  # fallback to original if parsing fails
    else:
        formatted_time = 'N/A'

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, f"Measurement Report: {data.get('name', 'N/A')}")

    # Time + Comment
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, height - 3 * cm, f"Date: {formatted_time}")
    c.drawString(2 * cm, height - 3.5 * cm, f"Comment: {data.get('comment', '')}")

    # EUT Config
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 5 * cm, "EUT Configuration:")
    c.setFont("Helvetica", 10)
    eut_y = height - 5.5 * cm
    for key, value in data.get("eutconfig", {}).items():
        if key == "Notes" and isinstance(value, str):
            value = value.replace('\n', '')
        c.drawString(2.5 * cm, eut_y, f"{key}: {value}")
        eut_y -= 0.5 * cm

    # Measurement Config
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, eut_y - 1 * cm, "Measurement Configuration:")
    mc_y = eut_y - 1.5 * cm
    c.setFont("Helvetica", 10)
    
    measurement_config = data.get("measurementconfig", {})
    for key, value in measurement_config.items():
        display_name = field_name_mapping.get(key, key)
        
        if key in ['fstart', 'fstop', 'fcenter', 'fspan'] and value is not None:
            value = f"{value / 1000000:.2f} MHz"
        elif key == 'rbw' and value is not None:
            value = f"{value / 1000:.1f} kHz"
        elif key == 'sweeptime' and value is not None:
            value = f"{value} s"
        
        c.drawString(2.5 * cm, mc_y, f"{display_name}: {value}")
        mc_y -= 0.4 * cm

    # Peaklist
    if data.get("peaklist", []):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, mc_y - 1 * cm, "Quasi-peaks:")
        pk_y = mc_y - 1.5 * cm
        c.setFont("Helvetica", 10)
        for peak in data.get("peaklist", []):
            freq_mhz = peak['freq'] / 1000000
            c.drawString(2.5 * cm, pk_y,
                        f"iid: {peak['iid']}, Frequency: {freq_mhz:.2f} MHz, "
                        f"Peak: {peak['pk']:.2f} dBµV, Quasi-peak: {peak['qpk']:.2f} dBµV, Limit: {peak['limit']}")
            pk_y -= 0.5 * cm


    if figure is not None:
        # Temp file to save the image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_image_path = tmp.name
        
        try:
            figure.savefig(temp_image_path, dpi=300, bbox_inches='tight', format='png')
            
            c.showPage()
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2 * cm, height - 2 * cm, "Measurement Plot")
            
            # Fit image to page
            img_width = width - 4 * cm
            img_height = height - 7 * cm
            
            c.drawImage(temp_image_path, 2 * cm, 10 * cm, 
                       width=img_width, height=img_height,
                       preserveAspectRatio=True, anchor='c')
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)


    c.save()

    print(f"Saved PDF to {pdf_path}")


field_name_mapping = {
    'fstart': 'Start frequency',
    'fstop': 'Stop frequency',
    'fcenter': 'Center frequency',
    'fspan': 'Frequency span',
    'sweeptime': 'Sweep time',
    'rbw': 'Resolution Bandwidth',
    'preamplifier': 'Preamplifier',
    'attenuation': 'Attenuation',
    'detector': 'Detector',
    'emifilter': 'EMI Filter',
    'sweepcount': 'Sweep count',
    'offset': 'Offset',
    'tracemode': 'Trace mode'
}