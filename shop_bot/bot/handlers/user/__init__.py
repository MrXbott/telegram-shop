from .addresses import router as addresses_router
from .cart import router as cart_router
from .catalog import router as catalog_router
from .favorites import router as favorites_router
from .orders import router as orders_router
from .products import router as products_router
from .settings import router as settings_router
from .start import router as start_router
from .support import router as support_router
from .payments import router as payments_router

routers = (
            addresses_router,
            cart_router, 
            catalog_router,
            favorites_router, 
            orders_router,
            products_router, 
            settings_router,
            start_router,
            support_router,
            payments_router
            )