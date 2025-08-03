"""
Script para procesar todos los documentos PDF de la JCE
Extrae información y la integra con el bot
"""

import os
import json
from datetime import datetime
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 no está instalado. Para procesar PDFs, ejecuta: pip install PyPDF2")

class DocumentProcessor:
    def __init__(self):
        self.documents_file = "jce_documents.json"
        self.load_documents()
    
    def load_documents(self):
        """Cargar documentos existentes"""
        if os.path.exists(self.documents_file):
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
        else:
            self.documents = {
                "leyes": {},
                "reglamentos": {},
                "resoluciones": {},
                "circulares": {},
                "manuales": {},
                "instrucciones": {},
                "fecha_actualizacion": datetime.now().isoformat()
            }
    
    def save_documents(self):
        """Guardar documentos actualizados"""
        self.documents["fecha_actualizacion"] = datetime.now().isoformat()
        with open(self.documents_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        print(f"✅ Documentos guardados en {self.documents_file}")
    
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
    
    def categorize_document(self, filename):
        """Categorizar documento según su nombre"""
        filename_lower = filename.lower()
        
        if "ley" in filename_lower:
            return "leyes"
        elif "reglamento" in filename_lower:
            return "reglamentos"
        elif "resolucion" in filename_lower or "res." in filename_lower:
            return "resoluciones"
        elif "circular" in filename_lower:
            return "circulares"
        elif "manual" in filename_lower:
            return "manuales"
        elif "instruccion" in filename_lower:
            return "instrucciones"
        else:
            return "otros"
    
    def extract_document_info(self, content, filename):
        """Extraer información del documento"""
        import re
        
        info = {
            "titulo": filename.replace('.pdf', ''),
            "numero": self.extract_number(content),
            "fecha": self.extract_date(content),
            "articulos": self.extract_articles(content),
            "capitulos": self.extract_chapters(content),
            "disposiciones": self.extract_dispositions(content),
            "contactos": self.extract_contacts(content),
            "palabras_clave": self.extract_keywords(content)
        }
        return info
    
    def extract_number(self, content):
        """Extraer número del documento"""
        import re
        patterns = [
            r'No\.?\s*(\d+)',
            r'Número\s*(\d+)',
            r'(\d+)-(\d{4})',
            r'Res\.\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return "No especificado"
    
    def extract_date(self, content):
        """Extraer fecha del documento"""
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
        """Extraer artículos del documento"""
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
    
    def extract_chapters(self, content):
        """Extraer capítulos del documento"""
        import re
        chapters = []
        pattern = r'Capítulo\s+(\d+)\.?\s*([^.]*\.)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for match in matches:
            chapters.append({
                "numero": match[0],
                "contenido": match[1].strip()
            })
        
        return chapters
    
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
    
    def extract_keywords(self, content):
        """Extraer palabras clave relevantes"""
        import re
        
        keywords = []
        relevant_terms = [
            "acta", "nacimiento", "cedula", "identidad", "matrimonio", 
            "divorcio", "naturalizacion", "apostilla", "registro civil",
            "junta central electoral", "jce", "documento", "tramite",
            "requisito", "costo", "tiempo", "oficina", "horario"
        ]
        
        content_lower = content.lower()
        for term in relevant_terms:
            if term in content_lower:
                keywords.append(term)
        
        return keywords
    
    def process_pdf_document(self, pdf_path):
        """Procesar un documento PDF"""
        if not PDF_AVAILABLE:
            print("❌ PyPDF2 no está disponible")
            return False
        
        try:
            # Extraer texto del PDF
            content = self.extract_text_from_pdf(pdf_path)
            if not content:
                return False
            
            # Obtener información del archivo
            filename = os.path.basename(pdf_path)
            category = self.categorize_document(filename)
            
            # Extraer información estructurada
            info = self.extract_document_info(content, filename)
            
            # Agregar a los documentos
            if category not in self.documents:
                self.documents[category] = {}
            
            self.documents[category][filename] = {
                "contenido": content,
                "informacion": info,
                "fuente": pdf_path,
                "fecha_procesamiento": datetime.now().isoformat(),
                "categoria": category,
                "formato": "PDF"
            }
            
            print(f"✅ Documento '{filename}' procesado y categorizado como '{category}'")
            return True
            
        except Exception as e:
            print(f"❌ Error procesando {pdf_path}: {e}")
            return False
    
    def process_all_documents(self, directory_path):
        """Procesar todos los PDFs de un directorio"""
        if not os.path.exists(directory_path):
            print(f"❌ Directorio no encontrado: {directory_path}")
            return False
        
        processed_count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                if self.process_pdf_document(file_path):
                    processed_count += 1
        
        print(f"✅ {processed_count} documentos procesados desde {directory_path}")
        return processed_count
    
    def generate_bot_responses(self):
        """Generar respuestas del bot basadas en los documentos"""
        bot_responses = {}
        
        for category, documents in self.documents.items():
            if category == "fecha_actualizacion":
                continue
                
            for filename, document in documents.items():
                info = document.get("informacion", {})
                
                # Crear respuesta estructurada
                response = f"📋 **Documento Oficial JCE**\n\n"
                response += f"**Título:** {info.get('titulo', filename)}\n"
                
                if info.get("numero"):
                    response += f"**Número:** {info['numero']}\n"
                
                if info.get("fecha"):
                    response += f"**Fecha:** {info['fecha']}\n"
                
                response += f"**Categoría:** {category.title()}\n\n"
                
                # Agregar artículos principales
                if info.get("articulos"):
                    response += "**Artículos principales:**\n"
                    for article in info["articulos"][:3]:
                        response += f"• Artículo {article['numero']}: {article['contenido'][:100]}...\n"
                    response += "\n"
                
                # Agregar capítulos
                if info.get("capitulos"):
                    response += "**Capítulos:**\n"
                    for chapter in info["capitulos"][:2]:
                        response += f"• Capítulo {chapter['numero']}: {chapter['contenido'][:100]}...\n"
                    response += "\n"
                
                # Agregar palabras clave
                if info.get("palabras_clave"):
                    response += "**Temas:** " + ", ".join(info["palabras_clave"][:5]) + "\n\n"
                
                response += "ℹ️ *Información basada en documentos oficiales de la JCE*"
                
                bot_responses[f"documento_{filename.lower().replace('.pdf', '').replace(' ', '_')}"] = response
        
        return bot_responses
    
    def generate_summary(self):
        """Generar resumen de todos los documentos"""
        summary = "📚 **Documentos JCE Procesados**\n\n"
        
        for category, documents in self.documents.items():
            if category == "fecha_actualizacion":
                continue
                
            summary += f"**{category.upper()}:**\n"
            for filename, document in documents.items():
                info = document.get("informacion", {})
                numero = info.get("numero", "N/A")
                fecha = info.get("fecha", "N/A")
                summary += f"• {filename} (No. {numero}, {fecha})\n"
            summary += "\n"
        
        return summary

def main():
    """Función principal"""
    if not PDF_AVAILABLE:
        print("❌ PyPDF2 no está instalado")
        print("💡 Para instalar: pip install PyPDF2")
        return
    
    processor = DocumentProcessor()
    
    print("📄 Procesador de Documentos JCE")
    print("=" * 40)
    
    # Procesar documentos
    documentos_dir = Path("documentos_jce")
    if documentos_dir.exists():
        processor.process_all_documents(str(documentos_dir))
    
    # Generar respuestas del bot
    bot_responses = processor.generate_bot_responses()
    
    # Guardar respuestas generadas
    with open("document_responses.py", 'w', encoding='utf-8') as f:
        f.write("# Respuestas basadas en documentos oficiales JCE\n")
        f.write("DOCUMENT_RESPONSES = {\n")
        for key, value in bot_responses.items():
            escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
            f.write(f'    "{key}": """{escaped_value}""",\n')
        f.write("}\n")
    
    # Generar resumen
    summary = processor.generate_summary()
    with open("documentos_summary.txt", 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # Guardar documentos
    processor.save_documents()
    
    print("\n🎉 Proceso completado!")
    print("📊 Estadísticas:")
    for category, documents in processor.documents.items():
        if category != "fecha_actualizacion":
            print(f"   {category}: {len(documents)}")
    
    print(f"\n📄 Resumen guardado en: documentos_summary.txt")
    print(f"🤖 Respuestas del bot en: document_responses.py")
    print(f"📋 Documentos en: {processor.documents_file}")

if __name__ == "__main__":
    main() 