import json
from datetime import datetime
import random
import os
import requests
import time
import logging
import anthropic

class PeiGoAgent:
    def __init__(self, api_key=None):
        # API Key para Claude
        self.api_key = "CLAUDE-AI-KEY"
        self.client = anthropic.Anthropic(api_key=self.api_key)
        if not self.api_key:
            raise ValueError("Se requiere una API Key para Claude. Proporcione api_key o configure CLAUDE_API_KEY en las variables de entorno.")
            
        
        # Cargar base de conocimiento
        self.knowledge_base = self.load_knowledge_base()
        
        # Historial de conversación para Claude
        self.claude_conversation = []
        
        # Historial de conversación para el usuario
        self.conversation_history = []
        
        # Estado actual del usuario
        self.user_state = {
            "name": None,
            "identified": False,
            "interests": [],
            "credit_simulations": [],
            "products_discussed": []
        }
        
        # Configurar logging
        self.logger = logging.getLogger("PeiGoAgent")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def load_knowledge_base(self):
        """Carga la base de conocimiento desde un archivo JSON"""
        try:
            with open("peigo_knowledge_base.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            # Si no existe, crear una base de conocimiento de ejemplo
            return self.create_sample_knowledge_base()

    def create_sample_knowledge_base(self):
        """Crea una base de conocimiento de ejemplo"""
        knowledge_base = {
            "faqs": [
                {
                    "question": "¿Qué es peiGo y cómo funciona?",
                    "answer": "peiGo es una aplicación que te permite gestionar tu dinero de forma fácil y segura. Con peiGo, puedes abrir una cuenta en minutos, obtener una tarjeta Visa Débito, enviar y pedir dinero, recargar tu cuenta, pagar servicios y hacer pagos con QR. Está respaldada por Banco Guayaquil."
                },
                {
                    "question": "¿Dónde está alojado mi dinero?",
                    "answer": "Tu dinero está seguro en una cuenta de ahorros básica alojada y respaldada por Banco Guayaquil."
                },
                {
                    "question": "¿Cómo puedo dividir gastos con peiGo?",
                    "answer": "Para dividir gastos con peiGo, abre la aplicación, ve a la sección de actividad, selecciona el movimiento, elige 'Dividir este gasto', selecciona contactos y confirma la división."
                },
                {
                    "question": "¿Qué es Google Pay y cómo funciona?",
                    "answer": "Google Pay es una aplicación de pagos móviles y billetera digital que permite almacenar tarjetas de crédito y débito en dispositivos Android para realizar compras en línea y en tiendas físicas."
                },
                {
                    "question": "¿Cómo pago con peiGo para ver los partidos en Zapping?",
                    "answer": "Ingresa a la app de peiGo, selecciona 'Pago de servicios', busca 'Zapping', ingresa tu número de cédula, elige el combo y completa el pago con validación biométrica."
                },
                {
                    "question": "¿Qué tipo de servicios puedo pagar en peiGo?",
                    "answer": "Puedes pagar recargas de celular, agua, luz, TV paga, internet, juegos, almacenes, y otros servicios como IESS, SRI y Registro Civil."
                },
                {
                    "question": "¿Qué es la tarjeta Mastercard peiGo?",
                    "answer": "Es una tarjeta de débito virtual vinculada a tu saldo peiGo, permitiendo compras en línea y pagos con Google Pay y Apple Pay."
                },
                {
                    "question": "¿Cómo actualizar mi correo electrónico en peiGo?",
                    "answer": "Ingresa a tu perfil en la app, selecciona 'Información personal', edita el correo, realiza la validación biométrica y confirma con un código OTP."
                },
                {
                    "question": "¿Qué son los cupones de peiGo?",
                    "answer": "Son códigos promocionales que se pueden redimir en la app para recibir dinero acreditado en tu cuenta."
                },
                {
                    "question": "¿Cómo funciona la mecánica de referidos en peiGo?",
                    "answer": "Invita amigos con tu link de referido y gana $1 cuando creen su cuenta y $1 adicional cuando realicen su primera transacción."
                },
                {
                    "question": "¿Cómo me registro en peiGo?",
                    "answer": "Descarga la app desde AppStore o Google Play, crea tu cuenta con tu documento de identidad ecuatoriano y un número de celular ecuatoriano."
                },
                {
                    "question": "¿Puedo pagar servicios en peiGo?",
                    "answer": "Sí, ingresa a la app, selecciona 'Pago de servicios', busca el servicio, ingresa los datos y confirma el pago."
                },
                {
                    "question": "¿Puedo agregar mi tarjeta virtual Visa peiGo a Google Pay?",
                    "answer": "Sí, puedes agregarla desde la app de peiGo o directamente desde Google Wallet siguiendo las instrucciones de verificación."
                },
                {
                    "question": "¿Es seguro usar Google Pay con mi tarjeta Visa peiGo?",
                    "answer": "Sí, Google Pay utiliza tecnología de tokenización que protege tu información al no compartir tu número real de tarjeta con los comerciantes."
                },
                {
                    "question": "¿Cómo puedo invitar a alguien a través del programa de referidos?",
                    "answer": "Comparte tu link de referido desde la app de peiGo con tus amigos."
                },
                {
                    "question": "¿Cuánto tiempo tarda en activarse mi código Zapping después del pago?",
                    "answer": "El código se genera inmediatamente y está disponible en la sección 'Actividad' de la app o en tu correo electrónico registrado."
                },
                {
                    "question": "¿Cuánto gano por cada referido exitoso?",
                    "answer": "Ganas hasta $2: $1 cuando tu amigo crea su cuenta y $1 adicional cuando realiza su primera transacción en peiGo."
                }
            ],
            "products": [
                {
                    "name": "Recarga Dinero",
                    "description": "¡Recarga rápido, fácil y sin costo! Las opciones que tienes para recargar son: tarjeta débito, cajero, Bancos del Barrio o cuentas bancarias. Selecciona la que prefieras."
                },
                {
                    "name": "Envía y recibe dinero",
                    "description": "Envía y recibe dinero al instante. Y lo mejor: ¡todo desde tu celular!"
                },
                {
                    "name": "Retira dinero",
                    "description": "¡Retira donde y cuando lo necesites! Con peiGo tu dinero está al alcance de tu mano, retíralo cuando desees en los diferentes puntos autorizados alrededor de todo Ecuador."
                },
                {
                    "name": "Divide Gastos",
                    "description": "¡Comparte el pago de la cuenta! Con peiGo pagas la cuenta y luego divides el gasto entre tus amigos. ¡Ahora lo único que te deberán será una próxima salida!"
                },
                {
                    "name": "Pago de Servicios",
                    "description": "¡Ya puedes pagar tus servicios desde peiGo! Paga agua, luz, internet, TV y hasta recarga saldo en tu celular y en juegos favoritos, directamente desde el app."
                },
                {
                    "name": "Tarjeta de Débito",
                    "description": "¡Tu primera Tarjeta de Débito virtual! Obtén tu Tarjeta de Débito peiGo y realiza compras nacionales e internacionales online, paga suscripciones y pide en tus apps favoritas. ¡Actívala gratis y en minutos!"
                },
                {
                    "name": "Tarjeta de Crédito",
                    "description": "¡Tu primera Tarjeta de Crédito virtual! Obtén tu Tarjeta de Crédito peiGo y realiza compras nacionales e internacionales online, paga suscripciones y pide en tus apps favoritas. ¡Actívala gratis y en minutos!"
                }
            ],
            "promotions": [
                {
                    "name": "Bienvenida 2025",
                    "description": "50% de descuento en comisiones para nuevos usuarios durante los primeros 3 meses",
                    "valid_until": "2025-06-30",
                    "code": "BIENVENIDA2025",
                    "details": "Aplica para todos los productos excepto PeiGo Home. El descuento se aplica automáticamente al utilizar el código promocional durante el registro."
                },
                {
                    "name": "Referidos Premium",
                    "description": "Recibe $500 por cada amigo que apruebe un crédito usando tu código de referido",
                    "valid_until": "2025-12-31",
                    "code": "AMIGO500",
                    "details": "Tu amigo debe completar su registro usando tu código y obtener la aprobación de un crédito mínimo de $5,000. El bono se depositará en tu cuenta 30 días después de la aprobación."
                }
            ],
            "credit_products": [
                {
                    "name": "Crédito Personal",
                    "interest_rate": 0.18,  # Tasa anual
                    "min_amount": 5000,
                    "max_amount": 50000,
                    "min_term": 6,  # meses
                    "max_term": 36,  # meses
                    "description": "Ideal para gastos personales, vacaciones, o imprevistos. Aprobación rápida y requisitos mínimos.",
                    "additional_fees": {"apertura": "2%", "seguro": "$250 mensual"}
                },
                {
                    "name": "Crédito Vehicular",
                    "interest_rate": 0.12,  # Tasa anual
                    "min_amount": 50000,
                    "max_amount": 500000,
                    "min_term": 12,  # meses
                    "max_term": 60,  # meses
                    "description": "Financiamiento para adquirir vehículos nuevos o seminuevos con tasas preferenciales y plazos cómodos.",
                    "additional_fees": {"apertura": "1.5%", "seguro": "Obligatorio, cotizado por separado"}
                },
                {
                    "name": "Crédito Hipotecario",
                    "interest_rate": 0.09,  # Tasa anual
                    "min_amount": 500000,
                    "max_amount": 5000000,
                    "min_term": 60,  # meses
                    "max_term": 240,  # meses
                    "description": "La mejor opción para adquirir tu vivienda con tasas competitivas y plazos extendidos.",
                    "additional_fees": {"apertura": "1%", "avalúo": "$5,000", "seguro": "0.3% anual sobre saldo"}
                }
            ]
        }
        
        # Guardar la base de conocimiento generada
        with open("peigo_knowledge_base.json", "w", encoding="utf-8") as file:
            json.dump(knowledge_base, file, indent=4, ensure_ascii=False)
            
        return knowledge_base

    def _construct_system_prompt(self):
        """Construye el prompt del sistema para Claude con la información de PeiGo"""
        # Convertir la base de conocimiento a formato de texto para incluirla en el prompt
        faqs_text = "\n".join([f"Pregunta: {faq['question']}\nRespuesta: {faq['answer']}" for faq in self.knowledge_base["faqs"]])
        
        products_text = ""
        for product in self.knowledge_base["products"]:
            products_text += f"\nProducto: {product['name']}\n"
            products_text += f"Descripción: {product['description']}\n"
        
        promotions_text = ""
        for promo in self.knowledge_base["promotions"]:
            promotions_text += f"\nPromoción: {promo['name']}\n"
            promotions_text += f"Descripción: {promo['description']}\n"
            promotions_text += f"Válido hasta: {promo['valid_until']}\n"
            promotions_text += f"Código: {promo['code']}\n"
            if 'details' in promo:
                promotions_text += f"Detalles: {promo['details']}\n"
        
        credit_products_text = ""
        for product in self.knowledge_base["credit_products"]:
            credit_products_text += f"\nProducto de crédito: {product['name']}\n"
            credit_products_text += f"Descripción: {product.get('description', 'No disponible')}\n"
            credit_products_text += f"Tasa de interés anual: {product['interest_rate']*100}%\n"
            credit_products_text += f"Monto mínimo: ${product['min_amount']}\n"
            credit_products_text += f"Monto máximo: ${product['max_amount']}\n"
            credit_products_text += f"Plazo mínimo: {product['min_term']} meses\n"
            credit_products_text += f"Plazo máximo: {product['max_term']} meses\n"
            if 'additional_fees' in product:
                fees = product['additional_fees']
                credit_products_text += "Comisiones adicionales:\n"
                for fee_name, fee_value in fees.items():
                    credit_products_text += f"- {fee_name.capitalize()}: {fee_value}\n"
        
        # Construcción del prompt del sistema
        system_prompt = f"""
Eres un agente de atención al cliente virtual de PeiGo, una innovadora plataforma financiera que ofrece soluciones de crédito personalizadas.

Tu misión es:
1. Responder preguntas sobre PeiGo utilizando la información proporcionada.
2. Actuar como asesor comercial, promoviendo las funcionalidades y productos de PeiGo.
3. Informar sobre promociones activas.
4. Explicar y simular productos de crédito, ayudando a los usuarios a comprender las opciones financieras.

CONOCIMIENTO SOBRE PEIGO:

PREGUNTAS FRECUENTES:
{faqs_text}

PRODUCTOS:
{products_text}

PROMOCIONES ACTIVAS:
{promotions_text}

PRODUCTOS DE CRÉDITO:
{credit_products_text}

INSTRUCCIONES DE COMPORTAMIENTO:
- Siempre sé amable, profesional y empático, orientado a brindar la mejor experiencia al cliente.
- Utiliza un lenguaje claro y sencillo, evitando tecnicismos financieros complejos a menos que sea necesario.
- Cuando promociones productos, destaca sus beneficios principales y cómo se adaptan a las necesidades del usuario.
- Si el usuario muestra interés en un producto, profundiza la información y ofrece una simulación de crédito.
- Si no conoces la respuesta a alguna pregunta específica, admítelo y ofrece poner al usuario en contacto con un agente humano.
- No inventes información que no esté en tu base de conocimiento.
- Mantén un tono conversacional y amigable, construyendo una relación de confianza con el usuario.
- Usa emojis ocasionalmente para hacer la conversación más amigable, pero mantén la profesionalidad.

Cuando hables sobre simulaciones de crédito, debes explicar claramente:
- Monto del préstamo
- Tasa de interés aplicada
- Plazo del crédito
- Pago mensual estimado
- Monto total a pagar
- Total de intereses generados

¡Estás listo para ayudar a los clientes de PeiGo!
"""
        return system_prompt

    def _get_claude_response(self, message):
        """Obtiene una respuesta de Claude a través de la API"""
        try:
            # Construir la conversación para Claude
            messages = self.claude_conversation.copy()
            
            # Añadir el mensaje actual del usuario
            messages.append({"role": "user", "content": message})
            
            # Realizar la solicitud
            response = self.client.messages.create(
                model="claude-3-opus-20240229", #"claude-3-7-sonnet-20250219",
                max_tokens=300,
                temperature=0.7,
                system=self._construct_system_prompt(),
                messages=messages
            )
            
            # Procesar la respuesta
            result = response.content
            assistant_message = result[0].text
            
            # Actualizar la conversación
            messages.append({"role": "assistant", "content": assistant_message})
            self.claude_conversation = messages
            
            return assistant_message
            
        except Exception as e:
            self.logger.error(f"Error al comunicarse con la API de Claude: {str(e)}")
            # Respuesta de fallback
            return "Lo siento, estoy experimentando problemas técnicos en este momento. Por favor, intenta de nuevo más tarde o contacta con nuestro equipo de soporte."

    def simulate_credit(self, product_name, amount, term):
        """Simula un producto de crédito"""
        # Buscar el producto de crédito
        product = None
        for p in self.knowledge_base["credit_products"]:
            if p["name"].lower() == product_name.lower():
                product = p
                break
        
        if not product:
            return {
                "success": False,
                "message": f"No se encontró el producto de crédito '{product_name}'"
            }
            
        # Validar monto y plazo
        if amount < product["min_amount"] or amount > product["max_amount"]:
            return {
                "success": False,
                "message": f"El monto debe estar entre ${product['min_amount']} y ${product['max_amount']}"
            }
            
        if term < product["min_term"] or term > product["max_term"]:
            return {
                "success": False,
                "message": f"El plazo debe estar entre {product['min_term']} y {product['max_term']} meses"
            }
            
        # Cálculo de la mensualidad (método francés)
        monthly_rate = product["interest_rate"] / 12
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
        
        # Construir tabla de amortización
        amortization_table = []
        remaining = amount
        
        for month in range(1, term + 1):
            interest = remaining * monthly_rate
            principal = monthly_payment - interest
            remaining -= principal
            
            amortization_table.append({
                "month": month,
                "payment": round(monthly_payment, 2),
                "principal": round(principal, 2),
                "interest": round(interest, 2),
                "remaining": round(max(0, remaining), 2)
            })
        
        # Guardar la simulación en el estado del usuario
        simulation = {
            "timestamp": datetime.now().isoformat(),
            "product": product_name,
            "amount": amount,
            "term": term,
            "monthly_payment": round(monthly_payment, 2),
            "total_payment": round(monthly_payment * term, 2),
            "total_interest": round((monthly_payment * term) - amount, 2)
        }
        
        self.user_state["credit_simulations"].append(simulation)
        
        return {
            "success": True,
            "simulation": simulation,
            "amortization_table": amortization_table
        }

    def extract_simulation_parameters(self, message):
        """Usa Claude para extraer parámetros de simulación de crédito del mensaje del usuario"""
        extraction_prompt = f"""
        Del siguiente mensaje del usuario, extrae los parámetros para una simulación de crédito.
        Si un parámetro no se menciona explícitamente, deja el valor como null.

        Mensaje del usuario: "{message}"

        Extrae los siguientes parámetros:
        1. Tipo de crédito (product_name): ¿Qué tipo de crédito solicita? (Crédito Personal, Crédito Automotriz, Crédito Hipotecario, etc.)
        2. Monto (amount): ¿Qué cantidad solicita?
        3. Plazo (term): ¿Por cuántos meses o años?

        Responde solo en formato JSON con esta estructura:
        {{"product_name": "nombre del producto o null", "amount": valor numérico o null, "term": valor numérico en meses o null}}
        """
        
        try:
             # Realizar la solicitud
            response = self.client.messages.create(
                model="claude-3-haiku-20240307", #"claude-3-7-sonnet-20250219",
                max_tokens=150,
                temperature=0.0,
                messages=[{"role": "user", "content": extraction_prompt}]
            )
            
            # Procesar la respuesta
            result = response.content
            assistant_message = result[0].text
            
            # Intentar extraer el JSON
            try:
                # Limpiar la respuesta por si Claude devuelve texto adicional
                json_str = assistant_message
                if "{" in assistant_message:
                    json_str = assistant_message[assistant_message.find("{"):assistant_message.rfind("}")+1]
                    
                parameters = json.loads(json_str)
                return parameters
            except json.JSONDecodeError:
                self.logger.error(f"Error al decodificar JSON de respuesta: {assistant_message}")
                return {"product_name": None, "amount": None, "term": None}
                
        except Exception as e:
            self.logger.error(f"Error al extraer parámetros: {str(e)}")
            return {"product_name": None, "amount": None, "term": None}

    def process_message(self, message, user_id="default_user"):
        """Procesa un mensaje del usuario y genera una respuesta utilizando Claude"""
        # Guardar el mensaje en el historial
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Detectar si es una simulación de crédito
        if any(keyword in message.lower() for keyword in ["simular", "simulación", "calcular", "préstamo", "crédito", "mensualidad"]):
            # Extraer parámetros para la simulación
            params = self.extract_simulation_parameters(message)
            
            # Si tenemos parámetros suficientes, realizar simulación
            if params.get("product_name") and params.get("amount") and params.get("term"):
                result = self.simulate_credit(
                    params["product_name"], 
                    float(params["amount"]), 
                    int(params["term"])
                )
                
                if result["success"]:
                    sim = result["simulation"]
                    response = f"He simulado un {params['product_name']} por ${params['amount']} a {params['term']} meses.\n\n" + \
                            f"Tu mensualidad sería de ${sim['monthly_payment']}.\n" + \
                            f"Pagarías un total de ${sim['total_payment']} al final del plazo.\n" + \
                            f"El interés total sería de ${sim['total_interest']}.\n\n" + \
                            "¿Te gustaría ver la tabla de amortización o ajustar los parámetros de la simulación?"
                else:
                    # Solicitar a Claude una respuesta más amigable para el error
                    error_prompt = f"""
                    Hubo un error en la simulación de crédito: "{result['message']}"
                    
                    Responde al usuario de manera amigable, explicando el error y pidiendo información adicional para realizar correctamente la simulación.
                    """
                    response = self._get_claude_response(error_prompt)
            else:
                # Pedir más información para la simulación
                missing_info_prompt = f"""
                El usuario quiere simular un crédito, pero falta información. De lo que pude entender:
                - Producto: {params.get('product_name', 'No especificado')}
                - Monto: {params.get('amount', 'No especificado')}
                - Plazo: {params.get('term', 'No especificado')}
                
                Responde amablemente pidiendo la información que falta para poder realizar la simulación. Menciona también los productos de crédito disponibles si el producto no fue especificado.
                """
                response = self._get_claude_response(missing_info_prompt)
        else:
            # Para otros mensajes, usar Claude directamente
            response = self._get_claude_response(message)
            
            # Actualizar productos discutidos si Claude menciona algún producto
            for product in self.knowledge_base["products"]:
                if product["name"] in response and product["name"] not in self.user_state["products_discussed"]:
                    self.user_state["products_discussed"].append(product["name"])
        
        # Guardar la respuesta en el historial
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response

    def generate_greeting(self):
        """Genera un saludo personalizado utilizando Claude"""
        greeting_prompt = """
        Genera un saludo amigable y profesional como agente virtual de PeiGo. 
        El saludo debe ser cálido, dar la bienvenida al usuario y ofrecer ayuda con productos financieros.
        Mantén el saludo breve (máximo 2 frases) y usa un emoji adecuado.
        """
        return self._get_claude_response(greeting_prompt)

    def generate_farewell(self):
        """Genera una despedida personalizada utilizando Claude"""
        farewell_prompt = """
        Genera una despedida amigable y profesional como agente virtual de PeiGo.
        Agradece al usuario por contactar a PeiGo y menciona que estamos disponibles para futuras consultas.
        Mantén la despedida breve (máximo 2 frases) y usa un emoji adecuado.
        """
        return self._get_claude_response(farewell_prompt)

    def generate_session_presentation(self):
        """Prepara datos para la generación de un PPT con la información de la sesión"""
        return {
            "success": True,
            "message": "Datos preparados para la generación de presentación",
            "user_state": self.user_state,
            "conversation_history": self.conversation_history
        }


# Ejemplo de uso simple
if __name__ == "__main__":
    # Verificar si hay API key
    api_key = "CLAUDE-AI-KEY"
    if not api_key:
        print(f"Presentación: {presentation['message']}")
        
    agent = PeiGoAgent(api_key=api_key)
    
    print("¡Agente PeiGo inicializado correctamente!")
    print("Simulando interacción...")
    
    # Simular algunas interacciones
    responses = [
        agent.process_message("Hola, ¿qué es PeiGo?"),
        agent.process_message("¿Qué productos ofrecen?"),
        agent.process_message("Me gustaría simular un crédito personal de $20,000 a 12 meses"),
        agent.process_message("¿Tienen alguna promoción activa?"),
        agent.process_message("Gracias, hasta luego")
    ]
    
    # Mostrar las respuestas
    for i, response in enumerate(responses):
        print(f"\nRespuesta {i+1}:\n{response}\n")
        