from django.contrib import admin
from .models import Med, District, Order,OrderDetails, Pharmacy, Concelho, Freguesy, Distributor, Warehouse, Product

admin.site.register(Med)
admin.site.register(District)
admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(Pharmacy)
admin.site.register(Concelho)
admin.site.register(Freguesy)
admin.site.register(Distributor)
admin.site.register(Warehouse)
admin.site.register(Product)

# Register your models here.
