#!python
try:
    import segno
    from PIL import Image
    QR_DEPS_AVAILABLE = True
    QR_LIBRARY = 'segno'
except ImportError:
    try:
        import qrcode
        from PIL import Image
        QR_DEPS_AVAILABLE = True
        QR_LIBRARY = 'qrcode'
    except ImportError:
        QR_DEPS_AVAILABLE = False
        QR_LIBRARY = None

def generate_qr(data, filename):
    """Generate QR code using available library"""
    if QR_LIBRARY == 'segno':
        qr = segno.make(data)
        qr.save(filename, scale=10)
        return True
    elif QR_LIBRARY == 'qrcode':
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        img.save(filename)
        return True
    return False

def decode_qr(filename):
    """Decode QR code - segno can only generate, so we need pyzbar for decoding"""
    # For decoding, we still need pyzbar or we can use zbar
    try:
        from pyzbar import pyzbar
        from PIL import Image
        img = Image.open(filename)
        decoded = pyzbar.decode(img)
        if decoded:
            return decoded[0].data.decode('utf-8')
    except:
        pass
    return None
