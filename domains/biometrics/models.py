from django.db import models

class BiometricProfile(models.Model):
    name = models.CharField(max_length=255)
    biometric_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Fingerprint(models.Model):
    profile = models.ForeignKey(BiometricProfile, on_delete=models.CASCADE)
    fingerprint_hash = models.TextField()

    def __str__(self):
        return f"Fingerprint - {self.profile.name}"


class FacialScan(models.Model):
    profile = models.ForeignKey(BiometricProfile, on_delete=models.CASCADE)
    image_path = models.CharField(max_length=255)

    def __str__(self):
        return f"Face Scan - {self.profile.name}"


class AccessLog(models.Model):
    profile = models.ForeignKey(BiometricProfile, on_delete=models.CASCADE)
    access_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.profile.name} - {self.status}"