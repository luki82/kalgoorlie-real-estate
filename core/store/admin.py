from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # This controls what columns you see when looking at your list of products
    list_display = ['title', 'category', 'price', 'is_active', 'created_at']
    
    # This adds a filter box on the right side to easily sort by category
    list_filter = ['is_active', 'category']
    
    # This lets you quickly change the price or toggle a product on/off without opening it
    list_editable = ['price', 'is_active']
    
    # This automatically types the URL slug for you based on your product title
    prepopulated_fields = {'slug': ('title',)}