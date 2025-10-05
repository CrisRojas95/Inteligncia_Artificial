# Importación de librerías necesarias
import random
import time
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Definición de enumeración para categorías de productos
class ProductCategory(Enum):
    """Enum que representa las diferentes categorías de productos disponibles"""
    ELECTRONICS = "Electrónicos"
    CLOTHING = "Ropa"
    BOOKS = "Libros"
    HOME = "Hogar"
    SPORTS = "Deportes"

# Clase de datos para representar productos
@dataclass
class Product:
    """
    Representa un producto en el marketplace
    Attributes:
        id: Identificador único del producto
        name: Nombre del producto
        category: Categoría a la que pertenece
        price: Precio del producto
        stock: Cantidad disponible en inventario
        seller_id: ID del vendedor dueño del producto
    """
    id: int
    name: str
    category: ProductCategory
    price: float
    stock: int
    seller_id: int

# Clase de datos para representar órdenes de compra
@dataclass
class Order:
    """
    Representa una orden de compra realizada por un cliente
    Attributes:
        order_id: Identificador único de la orden
        customer_id: ID del cliente que realizó la compra
        products: Lista de productos comprados
        total_amount: Monto total de la compra
        status: Estado actual de la orden
        timestamp: Fecha y hora de la compra
    """
    order_id: int
    customer_id: int
    products: List[Product]
    total_amount: float
    status: str
    timestamp: datetime

class CustomerAgent:
    """
    Agente que representa a un cliente en el sistema de e-commerce
    Maneja comportamiento de compra, presupuesto y preferencias
    """
    
    def __init__(self, agent_id: int, name: str, budget: float, preferences: List[ProductCategory]):
        """
        Inicializa un agente cliente
        Args:
            agent_id: Identificador único del cliente
            name: Nombre del cliente
            budget: Presupuesto disponible para compras
            preferences: Lista de categorías de productos preferidas
        """
        self.agent_id = agent_id
        self.name = name
        self.budget = budget
        self.preferences = preferences
        self.purchase_history = []  # Historial de compras realizadas
        self.shopping_cart = []     # Carrito de compras actual
    
    def browse_products(self, marketplace: 'Marketplace') -> List[Product]:
        """
        Navega por productos disponibles filtrados por preferencias y presupuesto
        Returns:
            Lista de productos que coinciden con criterios del cliente
        """
        available_products = marketplace.get_available_products()
        # Filtrar productos por preferencias y presupuesto
        preferred_products = [
            p for p in available_products 
            if p.category in self.preferences and p.price <= self.budget
        ]
        return preferred_products
    
    def add_to_cart(self, product: Product, marketplace: 'Marketplace') -> bool:
        """
        Agrega un producto al carrito de compras
        Returns:
            True si se pudo agregar, False en caso contrario
        """
        # Verificar stock y presupuesto antes de agregar
        if marketplace.check_stock(product.id) and product.price <= self.budget:
            self.shopping_cart.append(product)
            return True
        return False
    
    def remove_from_cart(self, product_id: int):
        """Remueve un producto del carrito basado en su ID"""
        self.shopping_cart = [p for p in self.shopping_cart if p.id != product_id]
    
    def view_cart(self) -> float:
        """
        Muestra el contenido actual del carrito y calcula el total
        Returns:
            Float con el total actual del carrito
        """
        total = sum(product.price for product in self.shopping_cart)
        print(f"\n🛒 Carrito de {self.name}")
        print("-" * 40)
        for i, product in enumerate(self.shopping_cart, 1):
            print(f"{i}. {product.name} - ${product.price:.2f}")
        print(f"Total: ${total:.2f}")
        print(f"Presupuesto disponible: ${self.budget:.2f}")
        return total
    
    def make_purchase(self, marketplace: 'Marketplace') -> bool:
        """
        Realiza la compra de los productos en el carrito
        Returns:
            True si la compra fue exitosa, False en caso contrario
        """
        total = self.view_cart()
        
        # Verificar que haya productos y presupuesto suficiente
        if total <= self.budget and self.shopping_cart:
            order = marketplace.process_order(self, self.shopping_cart)
            if order:
                # Actualizar presupuesto e historial
                self.budget -= total
                self.purchase_history.extend(self.shopping_cart.copy())
                self.shopping_cart.clear()
                return True
        return False

class SellerAgent:
    """
    Agente que representa a un vendedor en el marketplace
    Maneja productos, inventario y estrategias de venta
    """
    
    def __init__(self, agent_id: int, name: str):
        """
        Inicializa un agente vendedor
        Args:
            agent_id: Identificador único del vendedor
            name: Nombre del vendedor
        """
        self.agent_id = agent_id
        self.name = name
        self.products = []          # Lista de productos del vendedor
        self.sales_history = []     # Historial de ventas
    
    def add_product(self, product: Product):
        """Agrega un producto al inventario del vendedor"""
        self.products.append(product)
    
    def view_products(self):
        """Muestra todos los productos del vendedor con su información"""
        print(f"\n📦 Productos de {self.name}:")
        for product in self.products:
            print(f"  {product.name} - ${product.price:.2f} (Stock: {product.stock})")

class Marketplace:
    """
    Clase principal que coordina todos los agentes y funcionalidades del sistema
    Actúa como el entorno donde interactúan todos los agentes
    """
    
    def __init__(self):
        """Inicializa el marketplace con estructuras de datos vacías"""
        self.products = []              # Todos los productos disponibles
        self.orders = []                # Historial de órdenes
        self.customers = []             # Clientes registrados
        self.sellers = []               # Vendedores registrados
        self.order_counter = 1          # Contador para IDs de órdenes
        self.current_customer = None    # Cliente actualmente loggeado
    
    def register_customer(self, customer: CustomerAgent):
        """Registra un nuevo cliente en el marketplace"""
        self.customers.append(customer)
    
    def register_seller(self, seller: SellerAgent):
        """Registra un nuevo vendedor y agrega sus productos al marketplace"""
        self.sellers.append(seller)
        self.products.extend(seller.products)
    
    def add_product(self, product: Product):
        """Agrega un producto individual al marketplace"""
        self.products.append(product)
    
    def get_available_products(self) -> List[Product]:
        """Retorna lista de productos con stock disponible"""
        return [p for p in self.products if p.stock > 0]
    
    def check_stock(self, product_id: int) -> bool:
        """Verifica si un producto tiene stock disponible"""
        product = next((p for p in self.products if p.id == product_id), None)
        return product and product.stock > 0
    
    def process_order(self, customer: CustomerAgent, products: List[Product]) -> Order:
        """
        Procesa una orden de compra, actualizando inventarios y creando la orden
        Returns:
            Order object si fue exitosa, None en caso contrario
        """
        # Verificar stock para todos los productos
        for product in products:
            if not self.check_stock(product.id):
                return None
        
        # Crear nueva orden
        order = Order(
            order_id=self.order_counter,
            customer_id=customer.agent_id,
            products=products.copy(),
            total_amount=sum(p.price for p in products),
            status="COMPLETED",
            timestamp=datetime.now()
        )
        
        # Actualizar stock de productos
        for product in products:
            product.stock -= 1
        
        # Registrar orden y incrementar contador
        self.orders.append(order)
        self.order_counter += 1
        return order
    
    def display_products(self, products: List[Product] = None):
        """
        Muestra productos de forma formateada
        Args:
            products: Lista de productos a mostrar (None para todos disponibles)
        """
        if products is None:
            products = self.get_available_products()
        
        print(f"\n🛍️  Productos Disponibles ({len(products)}):")
        print("-" * 60)
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name}")
            print(f"   Categoría: {product.category.value}")
            print(f"   Precio: ${product.price:.2f}")
            print(f"   Stock: {product.stock}")
            print(f"   Vendedor: {self.get_seller_name(product.seller_id)}")
            print()
    
    def get_seller_name(self, seller_id: int) -> str:
        """Obtiene el nombre de un vendedor basado en su ID"""
        for seller in self.sellers:
            if seller.agent_id == seller_id:
                return seller.name
        return "Desconocido"
    
    def customer_menu(self):
        """Menú principal de interacción para clientes loggeados"""
        while True:
            print(f"\n{'='*50}")
            print(f"👤 MENÚ CLIENTE: {self.current_customer.name}")
            print(f"{'='*50}")
            print("1. 🛍️  Ver productos disponibles")
            print("2. 🔍 Ver productos por categoría")
            print("3. 🛒 Ver mi carrito")
            print("4. ➕ Agregar producto al carrito")
            print("5. ❌ Remover producto del carrito")
            print("6. 💳 Realizar compra")
            print("7. 📋 Ver mi historial de compras")
            print("8. 💰 Ver mi presupuesto")
            print("0. 👋 Cerrar sesión")
            
            choice = input("\nSelecciona una opción: ").strip()
            
            # Navegación por opciones del menú
            if choice == "1":
                self.display_products()
            
            elif choice == "2":
                self.category_menu()
            
            elif choice == "3":
                self.current_customer.view_cart()
            
            elif choice == "4":
                self.add_to_cart_menu()
            
            elif choice == "5":
                self.remove_from_cart_menu()
            
            elif choice == "6":
                self.make_purchase_menu()
            
            elif choice == "7":
                self.show_purchase_history()
            
            elif choice == "8":
                print(f"\n💰 Presupuesto actual: ${self.current_customer.budget:.2f}")
            
            elif choice == "0":
                print("¡Hasta pronto! 👋")
                break
            
            else:
                print("❌ Opción inválida. Intenta nuevamente.")
    
    def category_menu(self):
        """Menú para filtrar productos por categoría"""
        print("\n📂 Categorías disponibles:")
        for i, category in enumerate(ProductCategory, 1):
            print(f"{i}. {category.value}")
        
        try:
            cat_choice = int(input("\nSelecciona una categoría: ")) - 1
            if 0 <= cat_choice < len(ProductCategory):
                selected_category = list(ProductCategory)[cat_choice]
                # Filtrar productos por categoría seleccionada
                category_products = [p for p in self.get_available_products() 
                                   if p.category == selected_category]
                self.display_products(category_products)
            else:
                print("❌ Categoría inválida")
        except ValueError:
            print("❌ Ingresa un número válido")
    
    def add_to_cart_menu(self):
        """Menú para agregar productos al carrito"""
        products = self.get_available_products()
        if not products:
            print("❌ No hay productos disponibles")
            return
        
        self.display_products(products)
        
        try:
            product_choice = int(input("\nSelecciona el número del producto a agregar: ")) - 1
            if 0 <= product_choice < len(products):
                product = products[product_choice]
                if self.current_customer.add_to_cart(product, self):
                    print(f"✅ {product.name} agregado al carrito!")
                else:
                    print("❌ No se pudo agregar al carrito (sin stock o sin presupuesto)")
            else:
                print("❌ Número de producto inválido")
        except ValueError:
            print("❌ Ingresa un número válido")
    
    def remove_from_cart_menu(self):
        """Menú para remover productos del carrito"""
        if not self.current_customer.shopping_cart:
            print("❌ Tu carrito está vacío")
            return
        
        self.current_customer.view_cart()
        
        try:
            product_choice = int(input("\nSelecciona el número del producto a remover: ")) - 1
            if 0 <= product_choice < len(self.current_customer.shopping_cart):
                product = self.current_customer.shopping_cart[product_choice]
                self.current_customer.remove_from_cart(product.id)
                print(f"✅ {product.name} removido del carrito")
            else:
                print("❌ Número de producto inválido")
        except ValueError:
            print("❌ Ingresa un número válido")
    
    def make_purchase_menu(self):
        """Menú para procesar la compra del carrito"""
        if not self.current_customer.shopping_cart:
            print("❌ Tu carrito está vacío")
            return
        
        total = self.current_customer.view_cart()
        
        # Verificar presupuesto
        if total > self.current_customer.budget:
            print("❌ Presupuesto insuficiente para realizar la compra")
            return
        
        # Confirmación de compra
        confirm = input("\n¿Confirmar compra? (s/n): ").strip().lower()
        if confirm == 's':
            if self.current_customer.make_purchase(self):
                print("✅ ¡Compra realizada exitosamente!")
                print(f"📦 Número de orden: #{self.orders[-1].order_id}")
            else:
                print("❌ Error al procesar la compra")
        else:
            print("❌ Compra cancelada")
    
    def show_purchase_history(self):
        """Muestra el historial de compras del cliente actual"""
        if not self.current_customer.purchase_history:
            print("📝 Aún no has realizado compras")
            return
        
        print(f"\n📊 Historial de compras de {self.current_customer.name}:")
        print("-" * 50)
        for i, product in enumerate(self.current_customer.purchase_history, 1):
            print(f"{i}. {product.name} - ${product.price:.2f}")
    
    def seller_analysis_menu(self):
        """Menú que muestra análisis para vendedores"""
        print(f"\n{'='*50}")
        print("📈 ANÁLISIS PARA VENDEDORES")
        print(f"{'='*50}")
        
        # Mostrar análisis básico para cada vendedor
        for seller in self.sellers:
            print(f"\n🏪 Vendedor: {seller.name}")
            total_products = len(seller.products)
            total_stock = sum(product.stock for product in seller.products)
            total_value = sum(product.price * product.stock for product in seller.products)
            
            print(f"   Productos en venta: {total_products}")
            print(f"   Stock total: {total_stock} unidades")
            print(f"   Valor total del inventario: ${total_value:.2f}")
            
            # Mostrar productos con bajo stock
            low_stock_products = [p for p in seller.products if p.stock < 5]
            if low_stock_products:
                print(f"   ⚠️  Productos con stock bajo:")
                for product in low_stock_products:
                    print(f"      - {product.name} (Stock: {product.stock})")
    
    def login_menu(self) -> bool:
        """
        Menú de inicio de sesión para clientes
        Returns:
            True si el login fue exitoso, False en caso contrario
        """
        print(f"\n{'='*40}")
        print("🏪 SISTEMA MULTIAGENTE - E-COMMERCE")
        print(f"{'='*40}")
        
        # Verificar que hay clientes registrados
        if not self.customers:
            print("❌ No hay clientes registrados")
            return False
        
        print("\n👥 Clientes disponibles:")
        for i, customer in enumerate(self.customers, 1):
            print(f"{i}. {customer.name} (${customer.budget:.2f})")
        
        try:
            customer_choice = int(input("\nSelecciona tu usuario: ")) - 1
            if 0 <= customer_choice < len(self.customers):
                self.current_customer = self.customers[customer_choice]
                print(f"\n🎉 ¡Bienvenido/a, {self.current_customer.name}!")
                return True
            else:
                print("❌ Usuario inválido")
                return False
        except ValueError:
            print("❌ Ingresa un número válido")
            return False

def create_sample_data() -> tuple:
    """
    Función para crear datos de ejemplo del sistema
    Returns:
        Tuple con (sellers, customers, products)
    """
    # Crear vendedores de ejemplo
    seller1 = SellerAgent(1, "TechStore")
    seller2 = SellerAgent(2, "FashionHub")
    seller3 = SellerAgent(3, "BookWorld")
    
    # Crear productos de ejemplo
    products = [
        Product(1, "iPhone 15", ProductCategory.ELECTRONICS, 999.99, 5, 1),
        Product(2, "MacBook Pro", ProductCategory.ELECTRONICS, 1999.99, 3, 1),
        Product(3, "Auriculares Bluetooth", ProductCategory.ELECTRONICS, 79.99, 8, 1),
        Product(4, "Camiseta Nike", ProductCategory.CLOTHING, 29.99, 20, 2),
        Product(5, "Zapatos Deportivos", ProductCategory.CLOTHING, 89.99, 10, 2),
        Product(6, "Python Programming", ProductCategory.BOOKS, 39.99, 15, 3),
        Product(7, "Clean Code", ProductCategory.BOOKS, 49.99, 12, 3),
        Product(8, "Balón de Fútbol", ProductCategory.SPORTS, 25.99, 30, 2),
        Product(9, "Tablet Samsung", ProductCategory.ELECTRONICS, 299.99, 6, 1),
    ]
    
    # Asignar productos a vendedores
    for product in products:
        if product.seller_id == 1:
            seller1.add_product(product)
        elif product.seller_id == 2:
            seller2.add_product(product)
        else:
            seller3.add_product(product)
    
    # Crear clientes de ejemplo con diferentes preferencias y presupuestos
    customers = [
        CustomerAgent(1, "Ana García", 1500.00, 
                     [ProductCategory.ELECTRONICS, ProductCategory.BOOKS]),
        CustomerAgent(2, "Carlos López", 500.00, 
                     [ProductCategory.CLOTHING, ProductCategory.SPORTS]),
        CustomerAgent(3, "María Rodríguez", 3000.00, 
                     [ProductCategory.ELECTRONICS, ProductCategory.CLOTHING, 
                      ProductCategory.BOOKS, ProductCategory.SPORTS]),
    ]
    
    return [seller1, seller2, seller3], customers, products

def main():
    """
    Función principal que inicializa el sistema y maneja el menú principal
    """
    # Inicializar marketplace y cargar datos de ejemplo
    marketplace = Marketplace()
    sellers, customers, products = create_sample_data()
    
    # Registrar todos los participantes en el marketplace
    for seller in sellers:
        marketplace.register_seller(seller)
    
    for customer in customers:
        marketplace.register_customer(customer)
    
    # Bucle principal del sistema
    while True:
        print(f"\n{'#'*50}")
        print("🏪 MARKETPLACE MULTIAGENTE - MENÚ PRINCIPAL")
        print(f"{'#'*50}")
        print("1. 👤 Iniciar sesión como cliente")
        print("2. 📈 Análisis de vendedores")
        print("3. 📊 Ver estadísticas del marketplace")
        print("4. 🏪 Ver información de productos de vendedores")
        print("5. 🚪 Salir")
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == "1":
            if marketplace.login_menu():
                marketplace.customer_menu()
        
        elif choice == "2":
            marketplace.seller_analysis_menu()
        
        elif choice == "3":
            print(f"\n📊 ESTADÍSTICAS DEL MARKETPLACE")
            print(f"Clientes registrados: {len(marketplace.customers)}")
            print(f"Vendedores registrados: {len(marketplace.sellers)}")
            print(f"Productos disponibles: {len(marketplace.get_available_products())}")
            print(f"Órdenes procesadas: {len(marketplace.orders)}")
            
            if marketplace.orders:
                total_revenue = sum(order.total_amount for order in marketplace.orders)
                print(f"Ingresos totales: ${total_revenue:.2f}")
        
        elif choice == "4":
            print(f"\n🏪 INFORMACIÓN DE VENDEDORES")
            for seller in marketplace.sellers:
                seller.view_products()
        
        elif choice == "5":
            print("¡Gracias por usar el sistema! 👋")
            break
        
        else:
            print("❌ Opción inválida. Intenta nuevamente.")

if __name__ == "__main__":
    main()
