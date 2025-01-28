from django.db import models

# Create your models here.
class Category(models.Model):
    cname = models.CharField(max_length=30)
    
    class Meta:
        db_table = "Category"
        
    def __str__(self) ->str:
        return self.cname 
    
class Product(models.Model):
    product_name  = models.CharField(max_length=30)
    price = models.FloatField(default=200)
    description = models.CharField(max_length=70)
    image = models.ImageField(default='abc.jpg', upload_to='Images')
    quantity = models.IntegerField(default=20)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'Product'
    
    
    

  