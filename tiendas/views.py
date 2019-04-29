from inventario.views import ListView

from .filters import TiendaFilter

# Create your views here.


class TiendasView(ListView):
    permission_required = 'tiendas.view_tienda'
    template_name = 'base_lista.html'
    template_table = 'tiendas/tabla_body_tienda.html'
    paginate_by = 25
    extra_context = {'modelo': 'tienda', 'titulo': 'Lista de tiendas'}
    filter_ = TiendaFilter