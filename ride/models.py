from django.db import models

from accounts.models import CustomUser

# Create your models here.





class Payment(models.Model):
    
    destination = models.CharField(max_length=255)
    trip_time = models.DateTimeField()
    payment_by = models.ForeignKey(CustomUser, related_name='payments_made', on_delete=models.CASCADE)
    payment_to = models.ForeignKey(CustomUser, related_name='payments_received', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    date = models.DateField()


    def __str__(self):
        return f'{self.destination} - {self.price}'

 
class RideHistory(models.Model):
    user = models.IntegerField() 
    destination = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.destination
    def __str__(self):
        return self.destination
    

    