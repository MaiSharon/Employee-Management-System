from rest_framework import serializers
from dept_app import models

class TaskSerializer(serializers.ModelSerializer):
    level_display = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = ['id', 'level', 'level_display', 'title', 'detail']

    def get_level_display(self, obj):
        """
        顯示 Task 級別的選項文字。

        Returns:
            list of tuple: Task 級別的選項列表。每個元組格式為 (數字代碼, 文字描述)。

        Example:
            返回值示例：[(1, "重要"), (2, "普通"), (3, "閒置")]
        """
        return obj.get_level_display()
