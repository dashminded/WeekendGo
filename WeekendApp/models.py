from django.contrib.auth.models import User
from django.db import models
import json
# Create your models here.
# class college(models.Model):
#     college_name = models.CharField(max_length=50)
#     location = models.CharField(max_length=50)
#
#     class Meta:
#
#         db_table = 'college'


class owner(models.Model):
    owner_name = models.CharField(max_length=50)
    number = models.IntegerField()
    image = models.ImageField(upload_to='img/', default='/img/')


    class Meta:
        db_table = 'owner'

class pg(models.Model):
    pg_name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    rent = models.IntegerField()
    amenities = models.TextField()
    image = models.ImageField(upload_to='img/', default='/img/')
   # college = models.ForeignKey(college, on_delete=models.CASCADE, related_name="hostels")
    owner = models.ForeignKey(owner,on_delete=models.CASCADE)
    area = models.CharField(max_length=100, null=True, blank=True)
    beds = models.IntegerField(null=True, blank=True)
    baths= models.IntegerField(null=True, blank=True)

    nearest_police_station = models.CharField(max_length=150, null=True, blank=True)
    nearest_hospital = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.pg_name

    class Meta:
        db_table = 'pg'


from textblob import TextBlob
# class feedback(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     feedback = models.CharField(max_length=300)
#
#     def __str__(self):
#         return f"Feedback by {self.user.username}"
#
#     class Meta:
#         db_table = 'feedback'


class feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=300)
    sentiment = models.CharField(max_length=10, blank=True)  # positive/negative/neutral

    def __str__(self):
        return f"Feedback by {self.user.username}"

    def save(self, *args, **kwargs):
        # Perform sentiment analysis before saving
        analysis = TextBlob(self.feedback)
        if analysis.sentiment.polarity > 0:
            self.sentiment = 'positive'
        elif analysis.sentiment.polarity < 0:
            self.sentiment = 'negative'
        else:
            self.sentiment = 'neutral'
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'feedback'


class BookmarkItem(models.Model):
    cart = models.ForeignKey('bookmark', on_delete=models.CASCADE)
    product = models.ForeignKey(pg, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name}"


class bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pg = models.ForeignKey(pg,null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.pg.pg_name}"

    def remove_pg(self):
        """Removes the associated pg from the bookmark."""
        self.pg = None
        self.save()



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pg = models.ForeignKey(pg, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # final amount

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            days = (self.check_out - self.check_in).days
            if days < 1:  # safeguard
                days = 1
            self.amount = days * self.pg.rent
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user.username} at {self.pg.pg_name}"
