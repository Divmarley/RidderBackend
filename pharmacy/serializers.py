

from food.serializers import *
from pharmacy.models import *


class PharmacyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyCategory
        fields = '__all__'

class PharmacySerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    contact = ContactSerializer(many=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    promotions = PromotionSerializer(many=True, read_only=True) 

    class Meta:
        model = Pharmacy
        fields = '__all__'

    def create(self, validated_data):
        # print("validated_data",validated_data)
        location_data = validated_data.pop('location')
        contact_data = validated_data.pop('contact')
        location = Location.objects.create(**location_data)
        pharmacy = Pharmacy.objects.create(location=location, **validated_data)
        for contact in contact_data:
            contact_obj = Contact.objects.create(**contact)
            pharmacy.contact.add(contact_obj)
        return pharmacy

class PharmacyWithProductSerializer(serializers.ModelSerializer):
    pharmacy = PharmacySerializer()

    class Meta:
        model = PharmacyProduct
        fields = '__all__'

    # def create(self, validated_data):
    #     # print("validated_data",validated_data)
    #     location_data = validated_data.pop('location')
    #     contact_data = validated_data.pop('contact')
    #     location = Location.objects.create(**location_data)
    #     pharmacy = Pharmacy.objects.create(location=location, **validated_data)
    #     for contact in contact_data:
    #         contact_obj = Contact.objects.create(**contact)
    #         pharmacy.contact.add(contact_obj)
    #     return pharmacy



 

class PharmacyProductSerializer(serializers.ModelSerializer):
    # category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = PharmacyProduct
        fields = [
            'id', 'name', 'description', 'price', 'image',
            'order_type', 'inStock', 'requiresPrescription',
            'quantity', #'category_name', 'category',
        ]
        read_only_fields = ['id']