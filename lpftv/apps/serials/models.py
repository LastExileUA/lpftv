from django.conf import settings
from django.db import models
import Image, os

__docformat__ = "restructuredtext"

class CFilm(models.Model):
    """
    Base model for 'Movie' and 'Serial 
    """
    name = models.CharField(max_length = 50, verbose_name = "Serials' name")
    full_describe = models.TextField(verbose_name = "Full describe", blank = True)
    origin_img = models.ImageField(upload_to = "photos", blank = True) 
    last_img = models.ImageField(upload_to = "photos", editable = False, default = "")
    pub_date = models.DateTimeField()

    def get_small_url(self):
        """Return url to small image"""
        return self.origin_img.url[:self.origin_img.url.rindex('.')]+ \
            ".small"+self.origin_img.url[self.origin_img.url.rindex('.'):]

    def get_small_path(self):
        """Return path in local disk to small image"""
        return self.origin_img.path[:self.origin_img.path.rindex('.')]+ \
            ".small"+self.origin_img.path[self.origin_img.path.rindex('.'):]

    def get_last_img_path(self):
        """This function used only in pre_save()"""
        try:
            return self.last_img.path[:self.last_img.path.rindex('.')]+ \
                ".small"+self.last_img.path[self.last_img.path.rindex('.'):]
        except: '' 

    def save(self):
        """Saving small image 'size'x'size' in local disk"""
        models.Model.save(self)
        size = 200
        try:
            im = Image.open(self.origin_img.path)
            im.thumbnail((size, size), Image.ANTIALIAS)
            im.save(self.get_small_path(), "jpeg") 
        except IOError:
            print "Error"


    def pre_save(self):
        """Remove old images"""
        try: 
            if os.path.exists(self.get_last_img_path()):
                os.remove(self.get_last_img_path())
            if os.path.exists(self.last_img.path):
                os.remove(self.last_img.path)
        except: pass 
        self.last_img = self.origin_img

    def delete(self):
        """Remove images"""
        try:
            if os.path.exist(self.origin_img.path):
                os.remove(self.origin_img.path)
            if os.path.exists(self.get_small_path()):
                os.remove(self.get_small_path())
        except: pass

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)


def pre_save(sender, **kwargs):
    """Call 'pre_save()' to all objects what saving"""
    sobject = kwargs['instance']
    try:
        sobject.pre_save()
    except:
        None

class Serial(CFilm):
    """Contein serial describe and movie"""
    short_describe = models.TextField(verbose_name = "Short describe")

class Movie(CFilm):
    """It's only movie"""
    serial = models.ForeignKey(Serial)
    movie = models.FileField(upload_to = "serials")

models.signals.pre_save.connect(pre_save)

