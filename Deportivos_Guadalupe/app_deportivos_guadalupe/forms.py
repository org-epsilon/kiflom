from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit

from django import forms

from .models import Vehiculo


class SketchfabEmbedParser(HTMLParser):
    """Extracts the iframe and attribution links without accepting arbitrary HTML."""

    def __init__(self):
        super().__init__()
        self.iframe_attrs = {}
        self.links = []
        self._anchor = None
        self._anchor_text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'iframe' and not self.iframe_attrs:
            self.iframe_attrs = attributes
        elif tag == 'a' and len(self.links) < 5:
            self._anchor = attributes
            self._anchor_text = []

    def handle_data(self, data):
        if self._anchor is not None:
            self._anchor_text.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self._anchor is not None:
            self.links.append((self._anchor, ' '.join(''.join(self._anchor_text).split())))
            self._anchor = None
            self._anchor_text = []


def sanitize_sketchfab_embed(code):
    code = code.strip()
    if code.startswith('https://sketchfab.com/models/') and code.endswith('/embed'):
        code = f'<iframe title="Modelo 3D de Sketchfab" src="{escape(code, quote=True)}"></iframe>'
    parser = SketchfabEmbedParser()
    try:
        parser.feed(code)
    except Exception as error:
        raise forms.ValidationError('El código de Sketchfab no tiene un formato válido.') from error

    source = parser.iframe_attrs.get('src', '').strip()
    parsed_source = urlsplit(source)
    if (
        parsed_source.scheme != 'https'
        or parsed_source.netloc.lower() != 'sketchfab.com'
        or not parsed_source.path.startswith('/models/')
        or not parsed_source.path.endswith('/embed')
    ):
        raise forms.ValidationError(
            'El código debe contener un iframe de Sketchfab con una URL /models/.../embed.'
        )

    title = escape(parser.iframe_attrs.get('title', 'Modelo 3D de Sketchfab'))
    iframe = (
        f'<iframe title="{title}" src="{escape(source, quote=True)}" '
        'frameborder="0" allowfullscreen '
        'allow="autoplay; fullscreen; xr-spatial-tracking"></iframe>'
    )
    attribution_links = []
    for attrs, text in parser.links:
        href = attrs.get('href', '').strip()
        href_parts = urlsplit(href)
        if (
            href_parts.scheme == 'https'
            and href_parts.netloc.lower() == 'sketchfab.com'
            and text
        ):
            attribution_links.append(
                f'<a href="{escape(href, quote=True)}" target="_blank" '
                f'rel="nofollow noopener">{escape(text)}</a>'
            )
    attribution = ''
    if attribution_links:
        attribution = f'<p class="model-attribution">{" · ".join(attribution_links)}</p>'
    return f'<div class="sketchfab-embed-wrapper">{iframe}{attribution}</div>'


class DescriptionSanitizer(HTMLParser):
    allowed_tags = {
        'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'mark', 'sub', 'sup',
        'ul', 'ol', 'li', 'h2', 'h3', 'blockquote', 'pre', 'a', 'div',
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self._link_open = False

    def handle_starttag(self, tag, attrs):
        if tag not in self.allowed_tags:
            return
        if tag == 'a':
            href = dict(attrs).get('href', '')
            parsed_href = urlsplit(href)
            if parsed_href.scheme in {'http', 'https'} and parsed_href.netloc:
                self.output.append(
                    f'<a href="{escape(href, quote=True)}" target="_blank" rel="noopener nofollow">'
                )
                self._link_open = True
        elif tag == 'div':
            self.output.append('<p>')
        else:
            self.output.append(f'<{tag}>')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.output.append('<br>')

    def handle_endtag(self, tag):
        if tag == 'a':
            if self._link_open:
                self.output.append('</a>')
            self._link_open = False
        elif tag in self.allowed_tags and tag not in {'br'}:
            self.output.append(f'</{"p" if tag == "div" else tag}>')

    def handle_data(self, data):
        self.output.append(escape(data).replace('\n', '<br>'))


def sanitize_description(value):
    parser = DescriptionSanitizer()
    parser.feed(value or '')
    return ''.join(parser.output).strip()


class VehiculoForm(forms.ModelForm):
    limpiar_imagen = forms.BooleanField(label='Quitar imagen actual', required=False)
    limpiar_modelo_3d = forms.BooleanField(label='Quitar modelo 3D actual', required=False)
    modelo_3d_url = forms.CharField(
        label='Código embebido de Sketchfab',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 8,
            'placeholder': 'Pega aquí el código completo de Sketchfab <div>...</div>.',
        }),
    )

    class Meta:
        model = Vehiculo
        fields = [
            'marca', 'modelo', 'precio', 'anio', 'stock',
            'imagen_archivo', 'imagen_url', 'modelo_3d_archivo', 'modelo_3d_url',
            'combustible', 'motor', 'transmision', 'potencia', 'traccion',
            'carroceria', 'sillas', 'puertas', 'descripcion',
        ]
        labels = {
            'marca': 'Marca',
            'modelo': 'Nombre del vehículo',
            'precio': 'Precio (USD)',
            'anio': 'Modelo / año',
            'stock': 'Unidades disponibles',
            'imagen_archivo': 'Imagen del vehículo',
            'imagen_url': 'Enlace externo de imagen',
            'modelo_3d_archivo': 'Archivo 3D (.glb)',
            'modelo_3d_url': 'Código embebido de Sketchfab',
            'combustible': 'Tipo de combustible',
            'motor': 'Motor',
            'transmision': 'Transmisión',
            'potencia': 'Potencia / velocidad máxima',
            'traccion': 'Tracción',
            'carroceria': 'Tipo de carrocería',
            'sillas': 'Número de sillas',
            'puertas': 'Número de puertas',
            'descripcion': 'Descripción del vehículo',
        }
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'anio': forms.NumberInput(attrs={'min': '1886', 'max': '2100'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
            'combustible': forms.Textarea(attrs={'rows': 2}),
            'motor': forms.Textarea(attrs={'rows': 2}),
            'transmision': forms.Textarea(attrs={'rows': 2}),
            'potencia': forms.Textarea(attrs={'rows': 2}),
            'traccion': forms.Textarea(attrs={'rows': 2}),
            'carroceria': forms.Textarea(attrs={'rows': 2}),
            'sillas': forms.NumberInput(attrs={'min': '1', 'max': '20'}),
            'puertas': forms.NumberInput(attrs={'min': '0', 'max': '10'}),
            'descripcion': forms.Textarea(attrs={'rows': 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        image_file = cleaned_data.get('imagen_archivo')
        image_url = cleaned_data.get('imagen_url')
        model_file = cleaned_data.get('modelo_3d_archivo')
        model_embed_code = cleaned_data.get('modelo_3d_url')
        has_existing_image = bool(self.instance and (self.instance.imagen_archivo or self.instance.imagen_url))
        if not image_file and not image_url and not has_existing_image and not cleaned_data.get('limpiar_imagen'):
            raise forms.ValidationError('Añade una imagen mediante archivo o URL.')
        if image_file and not image_file.content_type.startswith('image/'):
            self.add_error('imagen_archivo', 'El archivo debe ser una imagen válida.')
        if model_file and not model_file.name.lower().endswith('.glb'):
            self.add_error('modelo_3d_archivo', 'El modelo 3D debe estar en formato .glb.')
        if model_file and model_embed_code:
            self.add_error('modelo_3d_url', 'Usa un archivo GLB o un código embebido, no ambos.')
        if model_embed_code:
            try:
                cleaned_data['modelo_3d_embed_html'] = sanitize_sketchfab_embed(model_embed_code)
            except forms.ValidationError as error:
                self.add_error('modelo_3d_url', error)
        return cleaned_data

    def clean_descripcion(self):
        return sanitize_description(self.cleaned_data.get('descripcion', ''))

    def save(self, commit=True):
        old_image_file = self.instance.imagen_archivo
        old_image_url = self.instance.imagen_url
        old_model_file = self.instance.modelo_3d_archivo
        old_model_url = self.instance.modelo_3d_url
        old_model_embed = self.instance.modelo_3d_embed_html
        vehicle = super().save(commit=False)
        if self.cleaned_data.get('limpiar_imagen'):
            vehicle.imagen_archivo = ''
            vehicle.imagen_url = ''
        elif not self.cleaned_data.get('imagen_archivo') and not self.cleaned_data.get('imagen_url'):
            vehicle.imagen_archivo = self.initial.get('imagen_archivo') or old_image_file
            vehicle.imagen_url = self.initial.get('imagen_url') or old_image_url
        if self.cleaned_data.get('limpiar_modelo_3d'):
            vehicle.modelo_3d_archivo = ''
            vehicle.modelo_3d_url = ''
            vehicle.modelo_3d_embed_html = ''
        elif self.cleaned_data.get('modelo_3d_archivo'):
            vehicle.modelo_3d_url = ''
            vehicle.modelo_3d_embed_html = ''
        elif self.cleaned_data.get('modelo_3d_embed_html'):
            vehicle.modelo_3d_archivo = ''
            vehicle.modelo_3d_embed_html = self.cleaned_data['modelo_3d_embed_html']
        elif not self.cleaned_data.get('modelo_3d_url'):
            vehicle.modelo_3d_archivo = self.initial.get('modelo_3d_archivo') or old_model_file
            vehicle.modelo_3d_url = self.initial.get('modelo_3d_url') or old_model_url
            vehicle.modelo_3d_embed_html = old_model_embed
        if commit:
            vehicle.save()
        return vehicle
from .models import Reporte

class ReporteForm (forms.ModelForm):
    class Meta: 
        model = Reporte
        fields = [
            'nombre',
            'descripcion',
            'foto',
            'documento',
            'audio',
            'video',
        ]