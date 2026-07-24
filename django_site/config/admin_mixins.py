"""Mixins compartilhados do Django Admin."""

from config.admin_docs import MODEL_DESCRIPTIONS


class DescriptiveAdminMixin:
    """Exibe texto de ajuda no changelist e no formulário de edição."""

    admin_description: str = ''
    change_list_template = 'admin/descriptive_change_list.html'
    change_form_template = 'admin/descriptive_change_form.html'

    def _admin_description(self):
        if self.admin_description:
            return self.admin_description
        key = f'{self.model._meta.app_label}.{self.model._meta.model_name}'
        return MODEL_DESCRIPTIONS.get(key, '')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_section_description'] = self._admin_description()
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_section_description'] = self._admin_description()
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_section_description'] = self._admin_description()
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
