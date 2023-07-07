from __future__ import absolute_import, unicode_literals  # 避免命名衝突


# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from prj_dept.celery import app as celery_app

__all__ = ('celery_app',)