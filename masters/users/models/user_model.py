from django.db import models
from django.utils import timezone
from django.db.models import Avg
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from ..validators import azerbaijani_letters_validator, mobile_number_validator
from ..user_managers import CustomUserManager

from services.models.category_model import Category
from services.models.service_model import Service
from reviews.models.review_models import Review
from core.models.city_model import City, District
from core.models.language_model import Language
from utils.validators import az_letters_validator



class CustomUser(AbstractBaseUser, PermissionsMixin):
    ##########//  Şəxsi məlumatlar  \\##########
    first_name = models.CharField(
        max_length=20,
        validators=[azerbaijani_letters_validator],
        verbose_name="Ad"
    )

    last_name = models.CharField(
        max_length=20,
        validators=[azerbaijani_letters_validator],
        verbose_name="Soyad"
    )

    birth_date = models.DateField(
        verbose_name="Doğum tarixi",
        help_text="Format: gün.ay.il (məsələn: 29.05.2025)"
    )

    mobile_number = models.CharField(
        max_length=9,
        unique=True,
        validators=[mobile_number_validator],
        verbose_name="Mobil nömrə"
    )

    GENDER_CHOICES = [
        ('MALE', 'Kişi'),
        ('FEMALE', 'Qadın')
    ]
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        verbose_name="Cins"
    )


    ##########//  Peşə məlumatları  \\##########
    profession_area = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='category_masters'
    )

    profession_speciality = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='profession_masters'
    )

    custom_profession = models.CharField(
        max_length=50,
        validators=[az_letters_validator],
        null=True,
        blank=True,
    )

    experience_years = models.PositiveIntegerField(
        verbose_name="İş təcrübəsi (il ilə)"
    )

    cities = models.ManyToManyField(
        City,
        related_name='city_masters',
        verbose_name='Şəhərlər',
        blank=True,
    )

    districts = models.ManyToManyField(
        District,
        related_name='district_masters',
        verbose_name='Bakı bölgələri',
        blank=True
    )

    ##########//  Təhsil məlumatları  \\##########
    EDUCATION_CHOICES = [
        ('0', 'Yoxdur'),
        ('1', 'Tam ali'),
        ('2', 'Natamam ali'),
        ('3', 'Orta'),
        ('4', 'Peşə təhsili'),
        ('5', 'Orta ixtisas təhsili'),
    ]
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        verbose_name="Təhsil səviyyəsi"
    )

    education_speciality = models.CharField(
        max_length=50,
        blank=True,
        validators=[az_letters_validator],
        verbose_name="Təhsil üzrə ixtisas"
    )

    languages = models.ManyToManyField(
        Language,
        verbose_name="Bildiyi dillər"
    )

    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name="Profil şəkli"
    )

    facebook = models.URLField(blank=True, verbose_name="Facebook linki")
    instagram = models.URLField(blank=True, verbose_name="Instagram linki")
    tiktok = models.URLField(blank=True, verbose_name="TikTok linki")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn linki")

    work_images = models.ManyToManyField(
        "WorkImage",
        blank=True,
        verbose_name="İşlərinə aid şəkillər"
    )

    note = models.TextField(
        validators=[az_letters_validator],
        blank=True,
        max_length=1500,
        verbose_name="Əlavə qeyd"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_master = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Yaradılma tarixi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son yenilənmə tarixi")

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = [] 

    objects = CustomUserManager()
    
    def average_rating(self):
        average = Review.objects.filter(master=self).aggregate(avg=Avg('rating'))['avg']
        if average is None:
            return ''
        return round(average, 2)

    @property
    def given_tags_with_count(self):
        tags = {
            "Təcrübəli": Review.objects.filter(master=self, experienced=True).count(),
            "Peşəkar": Review.objects.filter(master=self, professional=True).count(),
            "Səbirli": Review.objects.filter(master=self, patient=True).count(),
            "Dəqiq": Review.objects.filter(master=self, punctual=True).count(),
            "Məsuliyyətli": Review.objects.filter(master=self, responsible=True).count(),
            "Səliqəli": Review.objects.filter(master=self, neat=True).count(),
            "Vaxta nəzarət": Review.objects.filter(master=self, time_management=True).count(),
            "Ünsiyyətcil": Review.objects.filter(master=self, communicative=True).count(),
            "Səmərəli": Review.objects.filter(master=self, efficient=True).count(),
            "Çevik": Review.objects.filter(master=self, agile=True).count(),
        }
    
        return [name for name, count in tags.items() if count > 0]

    @property
    def review_count(self):
        return Review.objects.filter(master=self).count()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile_number})"