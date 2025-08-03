"""
Script para cargar documentos y expandir el conocimiento del bot
Permite agregar información desde archivos de texto, PDF, etc.
"""

import json
import os
from datetime import datetime

class DocumentLoader:
    def __init__(self):
        self.knowledge_file = "bot_knowledge.json"
        self.load_knowledge()
    
    def load_knowledge(self):
        """Cargar conocimiento existente"""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {
                "documentos": {},
                "preguntas_frecuentes": {},
                "procesos": {},
                "contactos": {},
                "fecha_actualizacion": datetime.now().isoformat()
            }
    
    def save_knowledge(self):
        """Guardar conocimiento actualizado"""
        self.knowledge["fecha_actualizacion"] = datetime.now().isoformat()
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
        print(f"✅ Conocimiento guardado en {self.knowledge_file}")
    
    def load_text_file(self, file_path, category="general"):
        """Cargar información desde archivo de texto"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer título del archivo
            title = os.path.basename(file_path).replace('.txt', '').replace('.md', '')
            
            # Agregar al conocimiento
            if "documentos" not in self.knowledge:
                self.knowledge["documentos"] = {}
            
            self.knowledge["documentos"][title] = {
                "contenido": content,
                "categoria": category,
                "fuente": file_path,
                "fecha_carga": datetime.now().isoformat()
            }
            
            print(f"✅ Documento '{title}' cargado desde {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar {file_path}: {e}")
            return False
    
    def load_from_directory(self, directory_path, category="general"):
        """Cargar todos los archivos de texto de un directorio"""
        if not os.path.exists(directory_path):
            print(f"❌ Directorio no encontrado: {directory_path}")
            return False
        
        loaded_count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith(('.txt', '.md')):
                file_path = os.path.join(directory_path, filename)
                if self.load_text_file(file_path, category):
                    loaded_count += 1
        
        print(f"✅ {loaded_count} documentos cargados desde {directory_path}")
        return loaded_count
    
    def extract_faqs_from_text(self, text):
        """Extraer preguntas frecuentes del texto"""
        faqs = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip().startswith('¿') and line.strip().endswith('?'):
                question = line.strip()
                # Buscar respuesta en la siguiente línea
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('R:'):
                    answer = lines[i + 1].strip()[2:].strip()
                    faqs.append((question, answer))
        
        return faqs
    
    def process_documents_for_faqs(self):
        """Procesar documentos para extraer FAQs automáticamente"""
        if "preguntas_frecuentes" not in self.knowledge:
            self.knowledge["preguntas_frecuentes"] = {}
        
        for title, doc_info in self.knowledge.get("documentos", {}).items():
            content = doc_info["contenido"]
            faqs = self.extract_faqs_from_text(content)
            
            for question, answer in faqs:
                self.knowledge["preguntas_frecuentes"][question] = {
                    "respuesta": answer,
                    "fuente": title,
                    "fecha_extraccion": datetime.now().isoformat()
                }
        
        print(f"✅ FAQs extraídas de documentos")
    
    def export_to_bot_format(self):
        """Exportar conocimiento en formato para el bot"""
        bot_responses = {}
        
        # Convertir documentos a respuestas del bot
        for title, doc_info in self.knowledge.get("documentos", {}).items():
            # Crear respuesta estructurada
            response = f"📄 {title}\n\n{doc_info['contenido'][:500]}..."
            bot_responses[title.lower()] = response
        
        # Convertir FAQs
        for question, info in self.knowledge.get("preguntas_frecuentes", {}).items():
            response = f"❓ {question}\n\n{info['respuesta']}"
            bot_responses[f"faq_{len(bot_responses)}"] = response
        
        return bot_responses
    
    def generate_bot_code(self):
        """Generar código Python para el bot con las nuevas respuestas"""
        bot_responses = self.export_to_bot_format()
        
        code = "# Respuestas generadas automáticamente\n"
        code += "RESPUESTAS_ADICIONALES = {\n"
        
        for key, value in bot_responses.items():
            # Escapar comillas en el valor
            escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
            code += f'    "{key}": """{escaped_value}""",\n'
        
        code += "}\n"
        
        # Guardar código generado
        with open("generated_responses.py", 'w', encoding='utf-8') as f:
            f.write(code)
        
        print("✅ Código generado en generated_responses.py")
        return code

def main():
    """Función principal"""
    loader = DocumentLoader()
    
    print("📚 Cargador de Documentos para el Bot")
    print("=" * 40)
    
    # Cargar documento de ejemplo
    if os.path.exists("documentos_jce.txt"):
        loader.load_text_file("documentos_jce.txt", "JCE")
        print("✅ Documento JCE cargado")
    
    # Procesar FAQs
    loader.process_documents_for_faqs()
    
    # Generar código para el bot
    loader.generate_bot_code()
    
    # Guardar conocimiento
    loader.save_knowledge()
    
    print("\n🎉 Proceso completado!")
    print("📊 Estadísticas:")
    print(f"   Documentos: {len(loader.knowledge.get('documentos', {}))}")
    print(f"   FAQs: {len(loader.knowledge.get('preguntas_frecuentes', {}))}")

if __name__ == "__main__":
    main() 