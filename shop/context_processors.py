from .models import Order


def cart_info(request):
    """Додає кількість товарів у кошику до кожного контексту."""
    cart_count = 0
    try:
        if request.session.session_key:
            order = Order.objects.filter(
                session_key=request.session.session_key,
                is_completed=False
            ).prefetch_related('items').first()
            if order:
                cart_count = order.get_total_items()
    except Exception:
        pass
    return {'cart_count': cart_count}
