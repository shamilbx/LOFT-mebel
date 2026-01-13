from .models import Cart, ProductCart, Product, Customer, Order, ProductOrder

# Класс с матода для работы с корзиной
class CartForAuthenticatedUser:
    def __init__(self, request, slug=None, action=None):
        self.user = request.user
        if slug and action:
            self.add_or_delete(slug, action)

    # Метод для получения информации о крзине и её товарах
    def get_cart_info(self):
        customer = Customer.objects.get(user=self.user)  # Получаем покупателя
        cart = Cart.objects.get(customer=customer)  # Получаем корзину покупателя
        products_cart = cart.productcart_set.all()
        return {
            'cart': cart,
            'products_cart': products_cart,
            'cart_price': cart.cart_total_price,
            'cart_quantity': cart.cart_total_quantity,
            'customer': customer
        }

    # Метод добавления товара в корзину, изменения его кол-ва удаления и очищения
    def add_or_delete(self, slug, action):
        cart = self.get_cart_info()['cart']
        product = Product.objects.get(slug=slug)
        product_cart, created = ProductCart.objects.get_or_create(cart=cart, product=product)  # Получить или создать

        if action == 'add' and product.quantity > 0 and product_cart.quantity < product.quantity:
            product_cart.quantity += 1
        elif action == 'delete':
            product_cart.quantity -= 1

        elif action == 'clear':
            product_cart.quantity = 0

        product_cart.save()

        if product_cart.quantity <= 0:
            product_cart.delete()

    # Метод сохранения и создания заказа покупателя
    def save_order(self, delivery):
        data = self.get_cart_info()
        order = Order.objects.create(customer=data['customer'], delivery=delivery,
                                     price=data['cart_price'], cart=data['cart'])
        order.save()
        for p_cart in data['products_cart']:
            product_order = ProductOrder.objects.create(order=order, name=p_cart.product.title,
                                                        slug=p_cart.product.slug,
                                                        price=p_cart.product.get_price(),
                                                        photo=p_cart.product.first_photo(),
                                                        total_price=p_cart.get_total_price, quantity=p_cart.quantity)
            product_order.save()

    # Метод очистки корзины
    def clear_cart(self):
        cart = self.get_cart_info()['cart']
        products_cart = cart.productcart_set.all()
        for p_cart in products_cart:
            product = p_cart.product
            product.quantity -= p_cart.quantity
            product.save()
            p_cart.delete()

        cart.save()



# Функция для получения информации о корзине
def cart_info(request):
    cart = CartForAuthenticatedUser(request)
    info = cart.get_cart_info()
    return info






