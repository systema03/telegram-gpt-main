"""
Script para entrenar el bot con conocimiento adicional
Permite agregar documentos, textos y información específica
"""

import json
import os
from datetime import datetime

class BotTrainer:
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
    
    def add_document_info(self, titulo, contenido, categoria="general"):
        """Agregar información de un documento"""
        if "documentos" not in self.knowledge:
            self.knowledge["documentos"] = {}
        
        self.knowledge["documentos"][titulo] = {
            "contenido": contenido,
            "categoria": categoria,
            "fecha_agregado": datetime.now().isoformat()
        }
        print(f"✅ Documento '{titulo}' agregado")
    
    def add_faq(self, pregunta, respuesta):
        """Agregar pregunta frecuente"""
        if "preguntas_frecuentes" not in self.knowledge:
            self.knowledge["preguntas_frecuentes"] = {}
        
        self.knowledge["preguntas_frecuentes"][pregunta] = {
            "respuesta": respuesta,
            "fecha_agregado": datetime.now().isoformat()
        }
        print(f"✅ FAQ agregada: {pregunta[:50]}...")
    
    def add_process(self, nombre, pasos, requisitos, tiempo, costo):
        """Agregar proceso específico"""
        if "procesos" not in self.knowledge:
            self.knowledge["procesos"] = {}
        
        self.knowledge["procesos"][nombre] = {
            "pasos": pasos,
            "requisitos": requisitos,
            "tiempo": tiempo,
            "costo": costo,
            "fecha_agregado": datetime.now().isoformat()
        }
        print(f"✅ Proceso '{nombre}' agregado")
    
    def add_contact(self, nombre, telefono, email, direccion):
        """Agregar contacto"""
        if "contactos" not in self.knowledge:
            self.knowledge["contactos"] = {}
        
        self.knowledge["contactos"][nombre] = {
            "telefono": telefono,
            "email": email,
            "direccion": direccion,
            "fecha_agregado": datetime.now().isoformat()
        }
        print(f"✅ Contacto '{nombre}' agregado")
    
    def search_knowledge(self, query):
        """Buscar en la base de conocimientos"""
        results = []
        query_lower = query.lower()
        
        # Buscar en documentos
        for titulo, info in self.knowledge.get("documentos", {}).items():
            if query_lower in titulo.lower() or query_lower in info["contenido"].lower():
                results.append(f"📄 {titulo}: {info['contenido'][:100]}...")
        
        # Buscar en FAQs
        for pregunta, info in self.knowledge.get("preguntas_frecuentes", {}).items():
            if query_lower in pregunta.lower() or query_lower in info["respuesta"].lower():
                results.append(f"❓ {pregunta}: {info['respuesta']}")
        
        return results
    
    def export_to_bot_format(self):
        """Exportar conocimiento en formato para el bot"""
        bot_knowledge = {}
        
        # Convertir documentos
        for titulo, info in self.knowledge.get("documentos", {}).items():
            bot_knowledge[titulo.lower()] = info["contenido"]
        
        # Convertir FAQs
        for pregunta, info in self.knowledge.get("preguntas_frecuentes", {}).items():
            bot_knowledge[f"faq_{len(bot_knowledge)}"] = f"P: {pregunta}\nR: {info['respuesta']}"
        
        return bot_knowledge

def main():
    """Función principal para entrenar el bot"""
    trainer = BotTrainer()
    
    print("🤖 Entrenador del Bot - Registro Civil RD")
    print("=" * 50)
    
    while True:
        print("\nOpciones:")
        print("1. Agregar información de documento")
        print("2. Agregar pregunta frecuente")
        print("3. Agregar proceso específico")
        print("4. Agregar contacto")
        print("5. Buscar en conocimiento")
        print("6. Ver estadísticas")
        print("7. Exportar conocimiento")
        print("8. Salir")
        
        opcion = input("\nSelecciona una opción (1-8): ")
        
        if opcion == "1":
            titulo = input("Título del documento: ")
            contenido = input("Contenido: ")
            categoria = input("Categoría (opcional): ")
            trainer.add_document_info(titulo, contenido, categoria)
            
        elif opcion == "2":
            pregunta = input("Pregunta: ")
            respuesta = input("Respuesta: ")
            trainer.add_faq(pregunta, respuesta)
            
        elif opcion == "3":
            nombre = input("Nombre del proceso: ")
            pasos = input("Pasos (separados por coma): ").split(",")
            requisitos = input("Requisitos (separados por coma): ").split(",")
            tiempo = input("Tiempo estimado: ")
            costo = input("Costo estimado: ")
            trainer.add_process(nombre, pasos, requisitos, tiempo, costo)
            
        elif opcion == "4":
            nombre = input("Nombre del contacto: ")
            telefono = input("Teléfono: ")
            email = input("Email: ")
            direccion = input("Dirección: ")
            trainer.add_contact(nombre, telefono, email, direccion)
            
        elif opcion == "5":
            query = input("Buscar: ")
            results = trainer.search_knowledge(query)
            if results:
                print(f"\nEncontrados {len(results)} resultados:")
                for result in results:
                    print(f"- {result}")
            else:
                print("No se encontraron resultados")
                
        elif opcion == "6":
            print(f"\n📊 Estadísticas:")
            print(f"Documentos: {len(trainer.knowledge.get('documentos', {}))}")
            print(f"Preguntas frecuentes: {len(trainer.knowledge.get('preguntas_frecuentes', {}))}")
            print(f"Procesos: {len(trainer.knowledge.get('procesos', {}))}")
            print(f"Contactos: {len(trainer.knowledge.get('contactos', {}))}")
            print(f"Última actualización: {trainer.knowledge.get('fecha_actualizacion', 'N/A')}")
            
        elif opcion == "7":
            bot_format = trainer.export_to_bot_format()
            with open("bot_knowledge_export.json", 'w', encoding='utf-8') as f:
                json.dump(bot_format, f, ensure_ascii=False, indent=2)
            print("✅ Conocimiento exportado a bot_knowledge_export.json")
            
        elif opcion == "8":
            trainer.save_knowledge()
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main() 