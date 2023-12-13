from rest_framework import serializers
from dept_app import models

class TaskSerializer(serializers.ModelSerializer):
    level_display = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = ['id', 'level', 'level_display', 'title', 'detail']

    def get_level_display(self, obj):
        """
        顯示 Task任務優先級的選項文字。

        Returns:
            list of tuple: Task任務優先級的選項文字列表。每個元組格式為 (數字代碼, 文字描述)。

        Example:
            返回值示例：[(1, "重要"), (2, "普通"), (3, "閒置")]
        """
        return obj.get_level_display()

    def validate_title(self, value):
        # 驗證標題長度
        if len(value) < 3:
            raise serializers.ValidationError("標題太短")
        return value

    def validate_detail(self, value):
        # 驗證詳細訊息的長度
        if len(value) > 50:
            raise serializers.ValidationError("詳細訊息太長")
        return value

    def validate(self, data):
        # 跨欄位的綜合驗證
        if '請款' in data['title'] and data['level'] != 1:
            raise serializers.ValidationError("請款的任務級別必須為 '重要'")
        return data