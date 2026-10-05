from django.test import TestCase
from django.urls import reverse

from .models import Vehiculo


class VehiculoCatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vehicle = Vehiculo.objects.create(
            marca='Nissan',
            modelo='GT-R Nismo',
            precio='210000',
            anio=2024,
            motor='3.8L V6 biturbo',
            stock=1,
            imagen_url='https://example.com/nissan.jpg',
            descripcion='Deportivo japonés.',
        )

    def test_brand_list_filters_by_brand(self):
        response = self.client.get(reverse('app_deportivos_guadalupe:car_branch_list', args=['nissan']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GT-R Nismo')

    def test_showcase_contains_vehicle_information(self):
        response = self.client.get(reverse('app_deportivos_guadalupe:car_showcase', args=[self.vehicle.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3.8L V6 biturbo')
        self.assertContains(response, 'Deportivo japonés.')
        self.assertContains(response, '$210.000')
        self.assertContains(response, 'Precio:')

    def test_catalog_lists_all_available_vehicles_newest_first(self):
        older = Vehiculo.objects.create(
            marca='Ferrari',
            modelo='F8 Tributo',
            precio='280000',
            anio=2023,
            imagen_url='https://example.com/ferrari.jpg',
        )
        response = self.client.get(reverse('app_deportivos_guadalupe:car_catalog'))

        self.assertEqual(response.status_code, 200)
        vehicles = list(response.context['vehicles'])
        self.assertEqual(vehicles[0], older)
        self.assertEqual(vehicles[1], self.vehicle)
        self.assertEqual(len(vehicles), Vehiculo.objects.filter(disponible=True).count())

    def test_create_vehicle_accepts_external_image_url(self):
        response = self.client.post(
            reverse('app_deportivos_guadalupe:car_create'),
            {
                'marca': 'Audi',
                'modelo': 'R8',
                'precio': '180000',
                'anio': '2024',
                'stock': '1',
                'imagen_url': 'https://example.com/audi.jpg',
                'combustible': 'Gasolina',
                'motor': '5.2L V10',
                'transmision': 'Automática',
                'potencia': '602 hp',
                'traccion': 'Integral',
                'carroceria': 'Coupé',
                'sillas': '2',
                'puertas': '2',
                'descripcion': 'Deportivo de altas prestaciones.',
            },
        )

        vehicle = Vehiculo.objects.get(marca='Audi', modelo='R8')
        self.assertRedirects(
            response,
            reverse('app_deportivos_guadalupe:car_showcase', args=[vehicle.id]),
        )

    def test_create_page_is_available(self):
        response = self.client.get(reverse('app_deportivos_guadalupe:car_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Publicar vehículo')

    def test_edit_page_updates_vehicle_and_preserves_media_when_omitted(self):
        response = self.client.get(
            reverse('app_deportivos_guadalupe:car_edit', args=[self.vehicle.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Guardar cambios')

        response = self.client.post(
            reverse('app_deportivos_guadalupe:car_edit', args=[self.vehicle.id]),
            {
                'marca': 'Nissan',
                'modelo': 'GT-R Nismo actualizado',
                'precio': '215000',
                'anio': '2025',
                'stock': '2',
                'combustible': 'Gasolina',
                'motor': '3.8L V6 biturbo',
                'sillas': '2',
                'puertas': '2',
                'descripcion': 'Ficha actualizada.',
            },
        )
        self.assertRedirects(
            response,
            reverse('app_deportivos_guadalupe:car_showcase', args=[self.vehicle.id]),
        )
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.modelo, 'GT-R Nismo actualizado')
        self.assertEqual(self.vehicle.descripcion, 'Ficha actualizada.')
        self.assertEqual(self.vehicle.imagen_url, 'https://example.com/nissan.jpg')

    def test_create_vehicle_sanitizes_sketchfab_embed_code(self):
        response = self.client.post(
            reverse('app_deportivos_guadalupe:car_create'),
            {
                'marca': 'Lamborghini',
                'modelo': 'Aventador SVJ',
                'precio': '500000',
                'anio': '2020',
                'stock': '1',
                'sillas': '2',
                'puertas': '2',
                'imagen_url': 'https://example.com/lamborghini.jpg',
                'modelo_3d_url': (
                    '<div class="sketchfab-embed-wrapper"><iframe '
                    'title="Lamborghini Aventador SVJ" '
                    'src="https://sketchfab.com/models/f5200e2c564a4ebab12c7e0f606a1303/embed">'
                    '</iframe><script>alert("blocked")</script></div>'
                ),
            },
        )

        vehicle = Vehiculo.objects.get(marca='Lamborghini')
        self.assertRedirects(
            response,
            reverse('app_deportivos_guadalupe:car_showcase', args=[vehicle.id]),
        )
        self.assertIn('sketchfab.com/models/f5200e2c564a4ebab12c7e0f606a1303/embed', vehicle.modelo_3d_embed_html)
        self.assertNotIn('<script', vehicle.modelo_3d_embed_html)
        showcase = self.client.get(
            reverse('app_deportivos_guadalupe:car_showcase', args=[vehicle.id])
        )
        self.assertContains(showcase, 'sketchfab-embed-wrapper')
        self.assertContains(showcase, 'f5200e2c564a4ebab12c7e0f606a1303/embed')
        self.assertNotContains(showcase, '<script')

    def test_create_vehicle_sanitizes_rich_description(self):
        response = self.client.post(
            reverse('app_deportivos_guadalupe:car_create'),
            {
                'marca': 'Porsche',
                'modelo': '911 GT3',
                'precio': '250000',
                'anio': '2025',
                'stock': '1',
                'sillas': '2',
                'puertas': '2',
                'imagen_url': 'https://example.com/porsche.jpg',
                'descripcion': '<p><strong>Rendimiento</strong></p><ul><li>Motor atmosférico</li></ul><script>alert(1)</script>',
            },
        )
        self.assertEqual(response.status_code, 302)
        vehicle = Vehiculo.objects.get(marca='Porsche', modelo='911 GT3')
        self.assertIn('<strong>Rendimiento</strong>', vehicle.descripcion)
        self.assertIn('<ul><li>Motor atmosférico</li></ul>', vehicle.descripcion)
        self.assertNotIn('<script', vehicle.descripcion)

    def test_rich_description_preserves_plain_text_paragraph_breaks(self):
        response = self.client.post(
            reverse('app_deportivos_guadalupe:car_create'),
            {
                'marca': 'BMW',
                'modelo': 'M4 Competition',
                'precio': '120000',
                'anio': '2025',
                'stock': '1',
                'sillas': '4',
                'puertas': '2',
                'imagen_url': 'https://example.com/bmw.jpg',
                'descripcion': 'Primera línea.\n\nSegunda línea.',
            },
        )
        self.assertEqual(response.status_code, 302)
        vehicle = Vehiculo.objects.get(marca='BMW', modelo='M4 Competition')
        self.assertIn('<br><br>', vehicle.descripcion)

# Create your tests here.
