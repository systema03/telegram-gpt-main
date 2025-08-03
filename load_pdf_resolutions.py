"""
Script para cargar resoluciones desde archivos PDF
Requiere: pip install PyPDF2
"""

import json
import os
from datetime import datetime
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 no está instalado. Para cargar PDFs, ejecuta: pip install PyPDF2")

class PDFResolutionLoader:
    def __init__(self):
        self.resolutions_file = "jce_resolutions.json"
        self.load_resolutions()
    
    def load_resolutions(self):
        """Cargar resoluciones existentes"""
        if os.path.exists(self.resolutions_file):
            with open(self.resolutions_file, 'r', encoding='utf-8') as f:
                self.resolutions = json.load(f)
        else:
            self.resolutions = {
                "resoluciones": {},
                "leyes": {},
                "reglamentos": {},
                "circulares": {},
                "fecha_actualizacion": datetime.now().isoformat()
            }
    
    def save_resolutions(self):
        """Guardar resoluciones actualizadas"""
        self.resolutions["fecha_actualizacion"] = datetime.now().isoformat()
        with open(self.resolutions_file, 'w', encoding='utf-8') as f:
            json.dump(self.resolutions, f, ensure_ascii=False, indent=2)
        print(f"✅ Resoluciones guardadas en {self.resolutions_file}")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extraer texto de un archivo PDF"""
        if not PDF_AVAILABLE:
            print("❌ PyPDF2 no está disponible")
            return None
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            print(f"❌ Error extrayendo texto de {pdf_path}: {e}")
            return None
    
    def load_pdf_resolution(self, pdf_path, category="resolucion"):
        """Cargar resolución desde archivo PDF"""
        if not PDF_AVAILABLE:
            print("❌ PyPDF2 no está disponible. Instala con: pip install PyPDF2")
            return False
        
        try:
            # Extraer texto del PDF
            content = self.extract_text_from_pdf(pdf_path)
            if not content:
                return False
            
            # Extraer información del archivo
            filename = os.path.basename(pdf_path)
            title = filename.replace('.pdf', '')
            
            # Procesar contenido (usar el mismo procesamiento que para TXT)
            processed_content = self.process_resolution_content(content, title)
            
            # Agregar a las resoluciones
            if category not in self.resolutions:
                self.resolutions[category] = {}
            
            self.resolutions[category][title] = {
                "contenido": content,
                "contenido_procesado": processed_content,
                "fuente": pdf_path,
                "fecha_carga": datetime.now().isoformat(),
                "tipo": category,
                "formato": "PDF"
            }
            
            print(f"✅ Resolución PDF '{title}' cargada desde {pdf_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar {pdf_path}: {e}")
            return False
    
    def process_resolution_content(self, content, title):
        """Procesar contenido de resolución (mismo que en load_resolutions.py)"""
        import re
        
        processed = {
            "titulo": title,
            "numero_resolucion": self.extract_resolution_number(content),
            "fecha": self.extract_date(content),
            "articulos": self.extract_articles(content),
            "disposiciones": self.extract_dispositions(content),
            "aplicacion": self.extract_application(content),
            "sanciones": self.extract_sanctions(content),
            "contactos": self.extract_contacts(content)
        }
        return processed
    
    def extract_resolution_number(self, content):
        """Extraer número de resolución"""
        import re
        patterns = [
            r'Resolución\s+No\.?\s*(\d+)',
            r'Resolución\s+(\d+)',
            r'No\.?\s*(\d+)',
            r'Res\.\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return "No especificado"
    
    def extract_date(self, content):
        """Extraer fecha de la resolución"""
        import re
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}-\d{1,2}-\d{4})',
            r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return "No especificada"
    
    def extract_articles(self, content):
        """Extraer artículos de la resolución"""
        import re
        articles = []
        pattern = r'Artículo\s+(\d+)\.?\s*([^.]*\.)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for match in matches:
            articles.append({
                "numero": match[0],
                "contenido": match[1].strip()
            })
        
        return articles
    
    def extract_dispositions(self, content):
        """Extraer disposiciones"""
        import re
        dispositions = []
        pattern = r'Disposición\s+(\w+)\.?\s*([^.]*\.)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for match in matches:
            dispositions.append({
                "tipo": match[0],
                "contenido": match[1].strip()
            })
        
        return dispositions
    
    def extract_application(self, content):
        """Extraer información sobre aplicación"""
        import re
        application_info = []
        
        sections = [
            "aplicación", "vigencia", "entrada en vigor", 
            "alcance", "ámbito de aplicación"
        ]
        
        for section in sections:
            pattern = rf'{section}[^.]*\.'
            matches = re.findall(pattern, content, re.IGNORECASE)
            application_info.extend(matches)
        
        return application_info
    
    def extract_sanctions(self, content):
        """Extraer información sobre sanciones"""
        import re
        sanctions = []
        pattern = r'sanción[^.]*\.'
        matches = re.findall(pattern, content, re.IGNORECASE)
        sanctions.extend(matches)
        return sanctions
    
    def extract_contacts(self, content):
        """Extraer información de contacto"""
        import re
        contacts = []
        
        # Buscar teléfonos
        phone_pattern = r'\(\d{3}\)\s*\d{3}-\d{4}'
        phones = re.findall(phone_pattern, content)
        contacts.extend([{"tipo": "telefono", "valor": phone} for phone in phones])
        
        # Buscar emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        contacts.extend([{"tipo": "email", "valor": email} for email in emails])
        
        return contacts
    
    def load_from_directory(self, directory_path, category="resolucion"):
        """Cargar todos los PDFs de un directorio"""
        if not os.path.exists(directory_path):
            print(f"❌ Directorio no encontrado: {directory_path}")
            return False
        
        loaded_count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                if self.load_pdf_resolution(file_path, category):
                    loaded_count += 1
        
        print(f"✅ {loaded_count} resoluciones PDF cargadas desde {directory_path}")
        return loaded_count

def main():
    """Función principal"""
    if not PDF_AVAILABLE:
        print("❌ PyPDF2 no está instalado")
        print("💡 Para instalar: pip install PyPDF2")
        return
    
    loader = PDFResolutionLoader()
    
    print("📄 Cargador de Resoluciones PDF - JCE")
    print("=" * 40)
    
    # Crear directorio para PDFs si no existe
    pdf_dir = Path("resoluciones_pdf")
    pdf_dir.mkdir(exist_ok=True)
    
    # Cargar PDFs existentes
    if pdf_dir.exists():
        loader.load_from_directory(str(pdf_dir), "resolucion")
    
    # Guardar resoluciones
    loader.save_resolutions()
    
    print("\n🎉 Proceso completado!")
    print("📊 Para agregar PDFs:")
    print("   1. Coloca los archivos PDF en la carpeta 'resoluciones_pdf'")
    print("   2. Ejecuta este script nuevamente")
    print("   3. El bot usará automáticamente la información de los PDFs")

if __name__ == "__main__":
    main() 