from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography import x509
import json
import codecs

def get_cert_data_in_json(cert_content, password):
    
    # Load the PKCS12 data
    private_key, certificate, additional_certs = load_key_and_certificates(
        cert_content, password.encode(), default_backend()
    )
    
    # Extract the private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Extract the certificate
    certificate_pem = certificate.public_bytes(encoding=serialization.Encoding.PEM)
    
    #=======================================
    
    # Lee el archivo del certificado PEM

    # Carga el certificado
    certificate = x509.load_pem_x509_certificate(certificate_pem, default_backend())

    # Obtiene el sujeto (usuario) del certificado
    subject = certificate.subject

    # Convierte los atributos del sujeto en un diccionario
    subject_dict = {attribute.oid._name: attribute.value for attribute in subject}
    
    # Corregir la codificación de todo el diccionario
    for key, value in subject_dict.items():
        try:
            subject_dict[key] = value.encode('latin-1').decode('utf-8')
        except UnicodeDecodeError:
            pass
    
    print(subject_dict)

    # Convierte el diccionario en formato JSON
    json_data = json.dumps(subject_dict, indent=4, ensure_ascii=False)
    
    print(json_data)
    
    return json_data
