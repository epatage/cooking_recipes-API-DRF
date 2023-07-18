import io

from rest_framework import renderers

INGREDIENT_DATA_FILE_HEADERS = ["Ingredient", "amount"]


class TextDataRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"

    def render(self, data, *arg, **kwargs):
        print(self.media_type)
        print(data)
        text_buffer = io.StringIO()
        text_buffer.write(
            ' '.join(header for header in INGREDIENT_DATA_FILE_HEADERS) + '\n'
        )

        for ingredient, value in data.items():
            print('ID', ingredient, value)
            text_buffer.write(
                ''.join(str(ingredient) + ' ' + str(value)) + '\n'
            )

        return text_buffer.getvalue()
