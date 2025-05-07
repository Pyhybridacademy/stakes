from django import forms

class TailwindTextInput(forms.TextInput):
    """
    Custom TextInput widget with Tailwind CSS styling.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class TailwindEmailInput(forms.EmailInput):
    """
    Custom EmailInput widget with Tailwind CSS styling.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'placeholder': 'you@email.com',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class TailwindPasswordInput(forms.PasswordInput):
    """
    Custom PasswordInput widget with Tailwind CSS styling.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'placeholder': '••••••••',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class TailwindTextarea(forms.Textarea):
    """
    Custom Textarea widget with Tailwind CSS styling.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'rows': 4
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class TailwindDateInput(forms.DateInput):
    """
    Custom DateInput widget with Tailwind CSS styling.
    """
    def __init__(self, attrs=None, format=None):
        default_attrs = {
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white',
            'type': 'date'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, format=format)


class TailwindFileInput(forms.ClearableFileInput):
    """
    Custom FileInput widget with Tailwind CSS styling.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'w-full px-3 py-2 border border-secondary-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)