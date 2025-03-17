# Agente Inteligente PeiGo
Este proyecto implementa un agente conversacional con GenAi utilizando el Api de Anthropic para brindar información sobre peiGo.

## 🎯 Funcionalidades

El agente es capaz de:

- ✅ Responder FAQs sobre PeiGo utilizando información extraída de su página web
- ✅ Actuar como asesor comercial, promoviendo y "vendiendo" las funcionalidades de PeiGo
- ✅ Informar sobre promociones activas, ayudando a los usuarios a aprovecharlas
- ✅ Simular el comportamiento de productos de crédito, incluyendo tablas de amortización y cálculos financieros
- ✅ Generar una presentación (PPT) automáticamente de la sesión del cliente con datos clave y visualizaciones

## 🛠️ Tecnologías utilizadas

- Python 3.8+
- Claude AI API para procesamiento de lenguaje natural
- python-pptx para generación de presentaciones
- Matplotlib para generación de gráficos

## 📋 Requisitos previos

1. Python 3.8 o superior
2. Clave API de Claude (Anthropic)
3. Paquetes Python listados en `requirements.txt`

## 💻 Uso

### Modo CLI (Interfaz de línea de comandos)

```bash
python peigo_cli_claude.py
```


### Ejemplos de interacción

1. **Preguntas sobre PeiGo**:
   - "¿Qué es PeiGo?"
   - "¿Cuáles son los requisitos para solicitar un crédito?"
   - "¿Tienen una aplicación móvil?"

2. **Consulta de productos**:
   - "¿Qué productos ofrecen?"
   - "Cuéntame sobre PeiGo Flex"
   - "¿Cuál es la mejor opción para un negocio pequeño?"

3. **Promociones activas**:
   - "¿Tienen alguna promoción actualmente?"
   - "¿Hay descuentos para nuevos clientes?"

4. **Simulaciones de crédito**:
   - "Quiero simular un crédito personal de $20,000 a 12 meses"
   - "¿Cuál sería la mensualidad para un crédito hipotecario de $2,000,000 a 15 años?"
   - "Necesito un préstamo para mi negocio de $500,000, ¿cuánto pagaría mensualmente a 5 años?"

## 📊 Generación de presentaciones

Al finalizar una conversación, el agente ofrecerá generar una presentación en PowerPoint que incluirá:
- Resumen de la interacción
- Productos discutidos
- Simulaciones de crédito realizadas con visualizaciones
- Análisis de la conversación

## 🧪 Pruebas

Para ejecutar las pruebas:
```bash
python -m unittest discover tests
```

## 📁 Estructura del proyecto

```
├── peigo_agent.py          # Clase principal del agente
├── presentation_generator.py # Generador de presentaciones
├── peigo_cli_claude.py            # Interfaz de línea de comandos
├── peigo_knowledge_base.json # Base de conocimiento
├── requirements.txt        # Dependencias
└── README.md               # Este archivo
```

## 👥 Autor

Desarrollado por Alvaro Junior Tellez.
