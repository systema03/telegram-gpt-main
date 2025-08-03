"""
Base de Conocimientos - Registro Civil República Dominicana
Este archivo contiene toda la información especializada para el bot
"""

# Información sobre tasas y costos actualizados
TASAS_JCE = {
    "acta_nacimiento": {
        "costo": "RD$ 500-800",
        "tiempo": "3-5 días hábiles",
        "documentos": [
            "Cédula de identidad del solicitante",
            "Si es para un menor: cédula de los padres",
            "Pago de la tasa correspondiente",
            "Solicitud en formulario oficial de la JCE"
        ]
    },
    "cambio_nombre": {
        "costo": "RD$ 1,500-2,000",
        "tiempo": "3-6 meses",
        "documentos": [
            "Solicitud formal con justificación",
            "Acta de nacimiento original",
            "Cédula de identidad",
            "Certificado de buena conducta",
            "Pago de tasas"
        ]
    },
    "naturalizacion": {
        "costo": "RD$ 5,000-8,000",
        "tiempo": "6-12 meses",
        "documentos": [
            "Residencia legal por 2 años",
            "Acta de nacimiento apostillada",
            "Certificado de buena conducta",
            "Certificado médico",
            "Pasaporte vigente",
            "Certificado de trabajo",
            "Comprobante de domicilio"
        ]
    },
    "cedula": {
        "primera_vez": "RD$ 400",
        "renovacion": "RD$ 300",
        "perdida": "RD$ 500",
        "tiempo": "15-30 días hábiles"
    },
    "matrimonio": {
        "costo": "RD$ 1,000-1,500",
        "tiempo": "3-4 semanas",
        "documentos": [
            "Acta de nacimiento (ambos)",
            "Cédula de identidad (ambos)",
            "Certificado de soltería",
            "Certificado médico"
        ]
    }
}

# Oficinas JCE por provincia
OFICINAS_JCE = {
    "Santo Domingo": {
        "direccion": "Av. 27 de Febrero",
        "telefono": "(809) 537-0100",
        "horarios": "8:00 AM - 4:00 PM"
    },
    "Santiago": {
        "direccion": "Av. Estrella Sadhalá",
        "telefono": "(809) 247-0100",
        "horarios": "8:00 AM - 4:00 PM"
    },
    "La Romana": {
        "direccion": "Av. Libertad",
        "telefono": "(809) 556-0100",
        "horarios": "8:00 AM - 4:00 PM"
    },
    "San Pedro": {
        "direccion": "Av. Independencia",
        "telefono": "(809) 246-0100",
        "horarios": "8:00 AM - 4:00 PM"
    }
}

# Información sobre procesos específicos
PROCESOS_ESPECIALES = {
    "adopcion": {
        "requisitos": [
            "Solicitud formal",
            "Certificado de idoneidad",
            "Acta de nacimiento del adoptado",
            "Sentencia de adopción",
            "Pago de tasas"
        ],
        "tiempo": "6-12 meses",
        "costo": "RD$ 3,000-5,000"
    },
    "divorcio": {
        "tipos": [
            "Divorcio por mutuo acuerdo",
            "Divorcio por incompatibilidad",
            "Divorcio por falta"
        ],
        "requisitos": [
            "Acta de matrimonio",
            "Cédulas de identidad",
            "Acuerdo de divorcio (si aplica)",
            "Pago de tasas"
        ],
        "tiempo": "2-6 meses",
        "costo": "RD$ 2,000-4,000"
    },
    "defuncion": {
        "requisitos": [
            "Certificado médico de defunción",
            "Cédula de identidad del fallecido",
            "Cédula de identidad del declarante",
            "Pago de tasas"
        ],
        "tiempo": "1-3 días hábiles",
        "costo": "RD$ 300-500"
    }
}

# Preguntas frecuentes
FAQ = {
    "¿Puedo obtener un acta de nacimiento si no tengo cédula?": "Sí, puedes usar tu pasaporte o cualquier documento de identidad válido.",
    "¿Cuánto tiempo tarda un cambio de nombre?": "El proceso completo toma entre 3-6 meses, incluyendo publicaciones y audiencia judicial.",
    "¿Puedo naturalizarme si solo tengo 1 año en RD?": "Solo si estás casado con un dominicano. Para otros casos necesitas 2 años de residencia.",
    "¿Qué documentos necesito para casarme con un extranjero?": "Necesitas su pasaporte y certificado de soltería apostillado de su país.",
    "¿Puedo renovar mi cédula antes de que expire?": "Sí, puedes renovarla hasta 6 meses antes de la fecha de vencimiento.",
    "¿Qué hago si perdí mi acta de nacimiento?": "Puedes solicitar una nueva en cualquier oficina de la JCE con tu cédula de identidad."
}

# Información de contacto y recursos
CONTACTOS_UTILES = {
    "JCE Central": {
        "telefono": "(809) 537-0100",
        "email": "info@jce.gob.do",
        "web": "www.jce.gob.do"
    },
    "Ministerio Relaciones Exteriores": {
        "telefono": "(809) 221-0100",
        "web": "www.mirex.gob.do"
    },
    "Policía Nacional": {
        "telefono": "911",
        "web": "www.policianacional.gob.do"
    }
} 