"""
Sistema para cargar resoluciones oficiales de la JCE
Permite procesar PDFs y documentos de texto para entrenar el bot
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

class ResolutionLoader:
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
    
    def load_text_resolution(self, file_path, category="resolucion"):
        """Cargar resolución desde archivo de texto"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer información del archivo
            filename = os.path.basename(file_path)
            title = filename.replace('.txt', '').replace('.md', '')
            
            # Procesar contenido para extraer información estructurada
            processed_content = self.process_resolution_content(content, title)
            
            # Agregar a las resoluciones
            if category not in self.resolutions:
                self.resolutions[category] = {}
            
            self.resolutions[category][title] = {
                "contenido": content,
                "contenido_procesado": processed_content,
                "fuente": file_path,
                "fecha_carga": datetime.now().isoformat(),
                "tipo": category
            }
            
            print(f"✅ Resolución '{title}' cargada desde {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar {file_path}: {e}")
            return False
    
    def process_resolution_content(self, content, title):
        """Procesar contenido de resolución para extraer información útil"""
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
        application_info = []
        
        # Buscar secciones relacionadas con aplicación
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
        sanctions = []
        pattern = r'sanción[^.]*\.'
        matches = re.findall(pattern, content, re.IGNORECASE)
        sanctions.extend(matches)
        return sanctions
    
    def extract_contacts(self, content):
        """Extraer información de contacto"""
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
    
    def create_bot_responses_from_resolutions(self):
        """Crear respuestas del bot basadas en las resoluciones"""
        bot_responses = {}
        
        for category, resolutions in self.resolutions.items():
            if category == "fecha_actualizacion":
                continue
                
            for title, resolution in resolutions.items():
                processed = resolution.get("contenido_procesado", {})
                
                # Crear respuesta estructurada
                response = f"📋 **{processed.get('titulo', title)}**\n\n"
                
                if processed.get("numero_resolucion"):
                    response += f"**Número:** {processed['numero_resolucion']}\n"
                
                if processed.get("fecha"):
                    response += f"**Fecha:** {processed['fecha']}\n\n"
                
                # Agregar artículos principales
                if processed.get("articulos"):
                    response += "**Artículos principales:**\n"
                    for article in processed["articulos"][:3]:  # Solo los primeros 3
                        response += f"• Artículo {article['numero']}: {article['contenido'][:100]}...\n"
                    response += "\n"
                
                # Agregar disposiciones
                if processed.get("disposiciones"):
                    response += "**Disposiciones:**\n"
                    for disp in processed["disposiciones"][:2]:  # Solo las primeras 2
                        response += f"• {disp['tipo']}: {disp['contenido'][:100]}...\n"
                    response += "\n"
                
                # Agregar información de aplicación
                if processed.get("aplicacion"):
                    response += "**Aplicación:**\n"
                    for app in processed["aplicacion"][:2]:
                        response += f"• {app[:100]}...\n"
                
                bot_responses[f"resolucion_{title.lower()}"] = response
        
        return bot_responses
    
    def generate_resolution_summary(self):
        """Generar resumen de todas las resoluciones"""
        summary = "📚 **Resoluciones JCE Cargadas**\n\n"
        
        for category, resolutions in self.resolutions.items():
            if category == "fecha_actualizacion":
                continue
                
            summary += f"**{category.upper()}:**\n"
            for title, resolution in resolutions.items():
                processed = resolution.get("contenido_procesado", {})
                numero = processed.get("numero_resolucion", "N/A")
                fecha = processed.get("fecha", "N/A")
                summary += f"• {title} (No. {numero}, {fecha})\n"
            summary += "\n"
        
        return summary
    
    def search_resolutions(self, query):
        """Buscar en las resoluciones"""
        results = []
        query_lower = query.lower()
        
        for category, resolutions in self.resolutions.items():
            if category == "fecha_actualizacion":
                continue
                
            for title, resolution in resolutions.items():
                content = resolution.get("contenido", "").lower()
                if query_lower in content or query_lower in title.lower():
                    processed = resolution.get("contenido_procesado", {})
                    results.append({
                        "titulo": title,
                        "categoria": category,
                        "numero": processed.get("numero_resolucion", "N/A"),
                        "fecha": processed.get("fecha", "N/A"),
                        "relevancia": content.count(query_lower)
                    })
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x["relevancia"], reverse=True)
        return results

def main():
    """Función principal"""
    loader = ResolutionLoader()
    
    print("📋 Cargador de Resoluciones JCE")
    print("=" * 40)
    
    # Crear directorio para resoluciones si no existe
    resolutions_dir = Path("resoluciones")
    resolutions_dir.mkdir(exist_ok=True)
    
    # Cargar resoluciones existentes
    if resolutions_dir.exists():
        for file_path in resolutions_dir.glob("*.txt"):
            loader.load_text_resolution(str(file_path), "resolucion")
    
    # Generar respuestas del bot
    bot_responses = loader.create_bot_responses_from_resolutions()
    
    # Guardar respuestas generadas
    with open("resolution_responses.py", 'w', encoding='utf-8') as f:
        f.write("# Respuestas basadas en resoluciones JCE\n")
        f.write("RESOLUTION_RESPONSES = {\n")
        for key, value in bot_responses.items():
            escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
            f.write(f'    "{key}": """{escaped_value}""",\n')
        f.write("}\n")
    
    # Generar resumen
    summary = loader.generate_resolution_summary()
    with open("resoluciones_summary.txt", 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # Guardar resoluciones
    loader.save_resolutions()
    
    print("\n🎉 Proceso completado!")
    print("📊 Estadísticas:")
    for category, resolutions in loader.resolutions.items():
        if category != "fecha_actualizacion":
            print(f"   {category}: {len(resolutions)}")
    
    print(f"\n📄 Resumen guardado en: resoluciones_summary.txt")
    print(f"🤖 Respuestas del bot en: resolution_responses.py")
    print(f"📋 Resoluciones en: {loader.resolutions_file}")

if __name__ == "__main__":
    main() 