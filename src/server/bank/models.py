from pathlib import Path

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete
from django.core.validators import FileExtensionValidator

# 1. Problems: id,title, statement, output, uploadedby
# 2. Admins: id, name, email, passwordhash
# 3. Students: id, name, email, passwordhash


@python_2_unicode_compatible
class Problem(models.Model):
    problem_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, unique=False)
    statement = models.TextField(max_length=3000, unique=False)
    problem_file = models.FileField(upload_to='bank/problem_files/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])], null=True, blank=True)
    uploadedby = models.ForeignKey(
        User,
        verbose_name="problem-setter",
        limit_choices_to={'is_staff': True},
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{} : {}".format(self.problem_id, self.title)

    class Meta:
        verbose_name = 'problem'
        ordering = ['problem_id']


@receiver(post_save, sender=Problem)
def check_config_count(sender, instance, **kwargs):
    testcase_dir = Path.cwd() / "bank/testcases" / str(instance.problem_id)
    testcase_dir.mkdir(parents=True, exist_ok=True)

@receiver(post_delete, sender=Problem)
def delete_testcases_folder(sender, instance, **kwargs):
    """ Deletes testcases folder of the deleted problem """

    testcase_dir = Path.cwd() / "bank/testcases" / str(instance.problem_id)
    if(testcase_dir.exists()):
        testcases_files = [f for f in testcase_dir.glob('**/*') if f.is_file()]
        for file in testcases_files:
            file.unlink()

        testcase_dir.rmdir()

@receiver(pre_delete, sender=Problem)
def delete_problem_file(sender, instance, **kwargs):
    problem = Problem.objects.get(problem_id=instance.problem_id)
    if not problem.problem_file:
        return
    problem_file = Path(str(problem.problem_file))
    problem_file.unlink()
