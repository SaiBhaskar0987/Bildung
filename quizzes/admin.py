from django.contrib import admin
from quizzes.models import UnansweredQuestion


@admin.register(UnansweredQuestion)
class UnansweredQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'is_answered', 'added_to_knowledge_base', 'asked_at']
    list_filter = ['is_answered', 'added_to_knowledge_base', 'asked_at']
    search_fields = ['question', 'answer']
    list_editable = ['is_answered']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('question', 'user', 'asked_at')
        }),
        ('Admin Response', {
            'fields': ('answer', 'is_answered', 'added_to_knowledge_base')
        }),
    )
    
    readonly_fields = ['asked_at']
    
    def question_preview(self, obj):
        return obj.question[:75] + "..." if len(obj.question) > 75 else obj.question
    question_preview.short_description = 'Question'
    
    actions = ['export_to_excel']
    
    def export_to_excel(self, request, queryset):
        import pandas as pd
        import io
        from core.settings import KNOWLEDGE_BASE_EXCEL_PATH
        
        questions = queryset.filter(is_answered=True, added_to_knowledge_base=False)
        
        if questions.count() < 15:
            self.message_user(request, f"Only {questions.count()} answered questions. Need 15 to export.", level='warning')
            return
        
        data = {
            'Question': [q.question for q in questions[:15]],
            'Answer': [q.answer for q in questions[:15]]
        }
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        
        try:
            existing_df = pd.read_excel(KNOWLEDGE_BASE_EXCEL_PATH)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
        except FileNotFoundError:
            combined_df = df
        
        combined_df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        questions[:15].update(added_to_knowledge_base=True)
        self.message_user(request, f"Exported 15 questions to Excel. Please update your embeddings.")

    
    export_to_excel.short_description = "Export 15 answered questions to Excel"
