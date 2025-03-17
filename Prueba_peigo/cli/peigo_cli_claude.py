import os
import sys
import argparse
import time
from datetime import datetime
from peigo_agent import PeiGoAgent
from presentation_generator import PresentationGenerator
from pyfiglet import Figlet
import logging
import dotenv

# Cargar variables de entorno desde .env si existe
dotenv.load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("peigo_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PeiGoCLI")

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_with_delay(text, delay=0.03):
    """Imprime texto con un efecto de escritura gradual"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def format_message(message, sender):
    """Formatea un mensaje para mostrarlo en la consola"""
    now = datetime.now().strftime("%H:%M:%S")
    if sender == "user":
        return f"\033[94m[Tú - {now}]\033[0m: {message}"
    else:  # sender == "assistant"
        return f"\033[92m[PeiGo - {now}]\033[0m: {message}"

def setup_arg_parser():
    """Configura el parser de argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='PeiGo Intelligent Agent with Claude AI')
    parser.add_argument('--api-key', type=str, help='Claude API Key (si no se establece en CLAUDE_API_KEY)')
    parser.add_argument('--debug', action='store_true', help='Activar modo debug')
    return parser

def main():
    # Configurar y parsear argumentos
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    # Configurar nivel de logging
    if args.debug:
        logger.setLevel(logging.DEBUG)
        
    # Obtener API key de Claude
    api_key = "CLAUDE-AI-API"
    if not api_key:
        print("ERROR: Se requiere una API Key para Claude. Proporciona --api-key o configura CLAUDE_API_KEY en las variables de entorno.")
        sys.exit(1)
    
    try:
        # Inicializar el agente
        agent = PeiGoAgent(api_key=api_key)
        logger.info("Agente PeiGo inicializado correctamente")
        
        # Configurar Figlet para el título
        f = Figlet(font='slant')
        
        # Iniciar la interfaz
        clear_screen()
        print(f.renderText('PeiGo Agent'))
        print("\033[93m" + "=" * 80 + "\033[0m")
        print_with_delay("¡Bienvenido al Asistente Virtual de PeiGo con Claude AI!")
        print_with_delay("Estoy aquí para ayudarte con información, productos, y simulaciones de crédito.")
        print_with_delay("Escribe 'salir' en cualquier momento para terminar la conversación.")
        print("\033[93m" + "=" * 80 + "\033[0m")
        print()
        
        # Mostrar primer mensaje del agente
        initial_greeting = agent.generate_greeting()
        print_with_delay(format_message(initial_greeting, "assistant"), delay=0.01)
        
        # Iniciar bucle de conversación
        conversation_active = True
        while conversation_active:
            # Obtener entrada del usuario
            user_input = input("\033[94m[Tú]\033[0m: ")
            
            # Verificar si el usuario quiere salir
            if user_input.lower() in ["salir", "adiós", "chao", "hasta luego", "exit", "quit"]:
                farewell = agent.generate_farewell()
                print_with_delay(format_message(farewell, "assistant"), delay=0.01)
                
                # Preguntar si quiere generar presentación
                print_with_delay("\n¿Deseas generar una presentación de esta sesión? (s/n): ", delay=0.01)
                generate_ppt = input().lower().strip()
                
                if generate_ppt == "s":
                    print_with_delay("Generando presentación...", delay=0.05)
                    
                    try:
                        # Crear generador de presentaciones
                        ppt_generator = PresentationGenerator()
                        
                        # Generar nombre de archivo único
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"PeiGo_Session_{timestamp}.pptx"
                        
                        # Generar la presentación
                        output_path = ppt_generator.generate_presentation(
                            agent.user_state, 
                            agent.conversation_history,
                            output_path=filename
                        )
                        
                        print_with_delay(f"¡Presentación generada con éxito! Guardada como: {output_path}", delay=0.03)
                    except Exception as e:
                        logger.error(f"Error al generar presentación: {e}")
                        print_with_delay("Lo siento, hubo un error al generar la presentación.", delay=0.03)
                
                print_with_delay("\n¡Gracias por usar el Asistente Virtual de PeiGo! ¡Hasta pronto!", delay=0.03)
                conversation_active = False
                continue
            
            # Procesar mensaje del usuario
            print(f"\033[93m[PeiGo está escribiendo...]\033[0m")
            response = agent.process_message(user_input)
            
            # Borrar el "está escribiendo"
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            
            # Mostrar respuesta del agente con efecto de escritura
            print_with_delay(format_message(response, "assistant"), delay=0.005)
            
            # Si el usuario ha realizado simulaciones, ofrecer más opciones
            if agent.user_state["credit_simulations"] and any(word in response.lower() for word in ["simulación", "mensualidad", "crédito"]):
                # Esperar un poco para no abrumar al usuario
                time.sleep(0.5)
                
                print_with_delay("\n\033[93m[Opciones disponibles]\033[0m:", delay=0.01)
                print_with_delay("1. Ver tabla de amortización", delay=0.01)
                print_with_delay("2. Modificar parámetros de simulación", delay=0.01)
                print_with_delay("3. Continuar conversación", delay=0.01)
                
                option = input("\nSelecciona una opción (1-3): ")
                
                if option == "1":
                    # Mostrar tabla de amortización de la última simulación
                    last_simulation = agent.user_state["credit_simulations"][-1]
                    product_name = last_simulation["product"]
                    amount = last_simulation["amount"]
                    term = last_simulation["term"]
                    
                    result = agent.simulate_credit(product_name, amount, term)
                    
                    if result["success"]:
                        print("\n\033[93m" + "=" * 80 + "\033[0m")
                        print(f"TABLA DE AMORTIZACIÓN - {product_name.upper()}")
                        print(f"Monto: ${amount} | Plazo: {term} meses | Mensualidad: ${last_simulation['monthly_payment']}")
                        print("\033[93m" + "=" * 80 + "\033[0m")
                        print(f"{'Mes':<5} {'Pago':<12} {'Capital':<12} {'Interés':<12} {'Saldo':<12}")
                        print("-" * 55)
                        
                        for row in result["amortization_table"]:
                            print(f"{row['month']:<5} ${row['payment']:<10} ${row['principal']:<10} ${row['interest']:<10} ${row['remaining']:<10}")
                            
                        print("\033[93m" + "=" * 80 + "\033[0m")
                        print(f"Total a pagar: ${last_simulation['total_payment']} | Total de intereses: ${last_simulation['total_interest']}")
                        print("\033[93m" + "=" * 80 + "\033[0m")
                
                elif option == "2":
                    # Solicitar nuevos parámetros para simulación
                    print_with_delay("\nModificar parámetros de simulación:", delay=0.01)
                    
                    # Mostrar productos disponibles
                    print("\nProductos disponibles:")
                    for i, product in enumerate(agent.knowledge_base["credit_products"]):
                        print(f"{i+1}. {product['name']} (Tasa: {product['interest_rate']*100}%)")
                    
                    # Solicitar selección de producto
                    product_idx = int(input("\nSelecciona un producto (número): ")) - 1
                    selected_product = agent.knowledge_base["credit_products"][product_idx]["name"]
                    
                    # Solicitar monto
                    amount = float(input("Monto del crédito: $"))
                    
                    # Solicitar plazo
                    term = int(input("Plazo en meses: "))
                    
                    # Realizar nueva simulación
                    result = agent.simulate_credit(selected_product, amount, term)
                    
                    if result["success"]:
                        sim = result["simulation"]
                        
                        # Solicitar a Claude que genere una respuesta amigable con la nueva simulación
                        simulation_prompt = f"""
                        He actualizado la simulación con estos nuevos parámetros:
                        - Producto: {selected_product}
                        - Monto: ${amount}
                        - Plazo: {term} meses
                        - Mensualidad: ${sim['monthly_payment']}
                        - Total a pagar: ${sim['total_payment']}
                        - Total de intereses: ${sim['total_interest']}
                        
                        Explica estos resultados de manera amigable y profesional, destacando los beneficios para el cliente.
                        """
                        
                        # Obtener respuesta de Claude
                        response = agent._get_claude_response(simulation_prompt)
                        print_with_delay(format_message(response, "assistant"), delay=0.01)
                    else:
                        print_with_delay(format_message(f"No pude realizar la simulación: {result['message']}", "assistant"), delay=0.01)
    
    except KeyboardInterrupt:
        print("\n\nPrograma terminado por el usuario. ¡Hasta pronto!")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"\n\nError inesperado: {e}")

if __name__ == "__main__":
    main()
