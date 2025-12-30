from django.db import models

class Scan(models.Model):
    SCAN_TYPE_CHOICES = [
        ('CKD', 'Chronic Kidney Disease (CKD)'),
        ('XRAY', 'X-Ray'),
        ('MRI', 'Magnetic Resonance Imaging (MRI)'),
        ('CT', 'Computed Tomography (CT Scan)'),
        ('ULTRASOUND', 'Ultrasound'),
        ('MAMMOGRAPHY', 'Mammography'),
        ('ECG', 'Electrocardiogram (ECG)'),
        ('OTHER', 'Other'),
    ]
    
    scan_type = models.CharField(
        max_length=20,
        choices=SCAN_TYPE_CHOICES,
        default='CKD',
        help_text='Select the type of medical scan'
    )
    image = models.ImageField(upload_to='scans/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='scans'
    )
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Medical Scan'
        verbose_name_plural = 'Medical Scans'
    
    def __str__(self):
        return f"{self.get_scan_type_display()} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

