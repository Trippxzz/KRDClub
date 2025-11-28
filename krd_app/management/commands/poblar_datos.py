"""
Comando de Django para poblar la base de datos con productos, vehículos y asociaciones.
Ejecutar con: python manage.py poblar_datos
"""
from django.core.management.base import BaseCommand
from krd_app.models import Producto, vehiculo, Producto_Vehiculo


class Command(BaseCommand):
    help = 'Pobla la base de datos con productos (llantas), vehículos y sus asociaciones'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de datos...\n')
        
        # ==================== PRODUCTOS (LLANTAS) ====================
        productos_data = [
            # Llantas deportivas premium
            {
                'n_producto': 'BBS SR Sport',
                'desc_producto': 'Llanta deportiva BBS SR de alto rendimiento con diseño multirradio. Ideal para vehículos deportivos europeos.',
                'stock': 24,
                'precio': 850000,
                'aro': 19,
                'apernadura': '5x112',
                'ancho': '8.5',
                'offset': 35,
                'centro_llanta': '66.6'
            },
            {
                'n_producto': 'OZ Racing Ultraleggera',
                'desc_producto': 'Llanta ultraligera OZ Racing con tecnología de fundición a baja presión. Máximo rendimiento en pista.',
                'stock': 16,
                'precio': 920000,
                'aro': 18,
                'apernadura': '5x112',
                'ancho': '8.0',
                'offset': 45,
                'centro_llanta': '57.1'
            },
            {
                'n_producto': 'Enkei RPF1',
                'desc_producto': 'Llanta Enkei RPF1 de competición. La elección de profesionales para track days y uso diario.',
                'stock': 20,
                'precio': 780000,
                'aro': 17,
                'apernadura': '5x100',
                'ancho': '7.5',
                'offset': 48,
                'centro_llanta': '73.1'
            },
            {
                'n_producto': 'Rotiform LAS-R',
                'desc_producto': 'Diseño clásico monoblock con acabado mate. Perfecta combinación de estilo y rendimiento.',
                'stock': 12,
                'precio': 650000,
                'aro': 19,
                'apernadura': '5x130',
                'ancho': '9.0',
                'offset': 45,
                'centro_llanta': '71.6'
            },
            {
                'n_producto': 'Vossen HF-5',
                'desc_producto': 'Llanta Vossen Hybrid Forged con diseño de 5 radios dobles. Lujo y rendimiento excepcional.',
                'stock': 8,
                'precio': 1200000,
                'aro': 20,
                'apernadura': '5x112',
                'ancho': '9.5',
                'offset': 40,
                'centro_llanta': '66.6'
            },
            {
                'n_producto': 'Work Emotion CR Kiwami',
                'desc_producto': 'Llanta japonesa Work de alto rendimiento. Fabricación flow forming de última generación.',
                'stock': 16,
                'precio': 890000,
                'aro': 18,
                'apernadura': '5x120',
                'ancho': '8.5',
                'offset': 38,
                'centro_llanta': '72.6'
            },
            {
                'n_producto': 'Rays Gram Lights 57DR',
                'desc_producto': 'Icónica llanta Rays de competición. Diseño clásico con tecnología moderna.',
                'stock': 12,
                'precio': 950000,
                'aro': 18,
                'apernadura': '5x112',
                'ancho': '8.0',
                'offset': 35,
                'centro_llanta': '57.1'
            },
            {
                'n_producto': 'ADV.1 ADV5.0',
                'desc_producto': 'Llanta forjada de lujo ADV.1 con diseño de 5 brazos. Exclusividad y rendimiento premium.',
                'stock': 8,
                'precio': 1500000,
                'aro': 21,
                'apernadura': '5x130',
                'ancho': '10.0',
                'offset': 42,
                'centro_llanta': '71.6'
            },
            {
                'n_producto': 'HRE FF04',
                'desc_producto': 'Llanta HRE FlowForm con diseño clásico de múltiples radios. Calidad americana premium.',
                'stock': 10,
                'precio': 1100000,
                'aro': 19,
                'apernadura': '5x112',
                'ancho': '9.0',
                'offset': 45,
                'centro_llanta': '66.6'
            },
            {
                'n_producto': 'TSW Bathurst',
                'desc_producto': 'Diseño inspirado en carreras con acabado hipersilver. Excelente relación calidad-precio.',
                'stock': 28,
                'precio': 520000,
                'aro': 18,
                'apernadura': '5x112',
                'ancho': '8.0',
                'offset': 42,
                'centro_llanta': '66.6'
            },
            {
                'n_producto': 'Vorsteiner V-FF 103',
                'desc_producto': 'Llanta flow forged Vorsteiner con diseño aerodinámico. Perfecta para sedanes de alto rendimiento.',
                'stock': 12,
                'precio': 980000,
                'aro': 19,
                'apernadura': '5x120',
                'ancho': '8.5',
                'offset': 35,
                'centro_llanta': '72.6'
            },
            {
                'n_producto': 'Brixton Forged RF7',
                'desc_producto': 'Llanta Brixton de lujo con diseño de radios split. Fabricación americana de alta calidad.',
                'stock': 6,
                'precio': 1350000,
                'aro': 20,
                'apernadura': '5x130',
                'ancho': '9.5',
                'offset': 50,
                'centro_llanta': '71.6'
            },
        ]

        # Crear productos
        productos_creados = []
        for prod_data in productos_data:
            prod, created = Producto.objects.get_or_create(
                n_producto=prod_data['n_producto'],
                defaults=prod_data
            )
            productos_creados.append(prod)
            status = 'CREADO' if created else 'YA EXISTE'
            self.stdout.write(f'  [{status}] Producto: {prod.n_producto}')

        self.stdout.write(self.style.SUCCESS(f'\n✓ {len(productos_creados)} productos procesados\n'))

        # ==================== VEHÍCULOS ====================
        vehiculos_data = [
            # Audi
            {'marca': 'Audi', 'modelo': 'A3', 'cilindrada': 1.4, 'anio': 2020},
            {'marca': 'Audi', 'modelo': 'A3', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'Audi', 'modelo': 'A4', 'cilindrada': 2.0, 'anio': 2020},
            {'marca': 'Audi', 'modelo': 'A4', 'cilindrada': 2.0, 'anio': 2022},
            {'marca': 'Audi', 'modelo': 'A5', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'Audi', 'modelo': 'A6', 'cilindrada': 3.0, 'anio': 2022},
            {'marca': 'Audi', 'modelo': 'Q5', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'Audi', 'modelo': 'Q7', 'cilindrada': 3.0, 'anio': 2023},
            {'marca': 'Audi', 'modelo': 'RS3', 'cilindrada': 2.5, 'anio': 2022},
            {'marca': 'Audi', 'modelo': 'RS6', 'cilindrada': 4.0, 'anio': 2023},
            
            # BMW
            {'marca': 'BMW', 'modelo': 'Serie 3', 'cilindrada': 2.0, 'anio': 2020},
            {'marca': 'BMW', 'modelo': 'Serie 3', 'cilindrada': 2.0, 'anio': 2022},
            {'marca': 'BMW', 'modelo': 'Serie 4', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'BMW', 'modelo': 'Serie 5', 'cilindrada': 3.0, 'anio': 2022},
            {'marca': 'BMW', 'modelo': 'M3', 'cilindrada': 3.0, 'anio': 2022},
            {'marca': 'BMW', 'modelo': 'M4', 'cilindrada': 3.0, 'anio': 2023},
            {'marca': 'BMW', 'modelo': 'X3', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'BMW', 'modelo': 'X5', 'cilindrada': 3.0, 'anio': 2022},
            {'marca': 'BMW', 'modelo': 'X6', 'cilindrada': 4.4, 'anio': 2023},
            
            # Mercedes-Benz
            {'marca': 'Mercedes-Benz', 'modelo': 'Clase A', 'cilindrada': 1.3, 'anio': 2020},
            {'marca': 'Mercedes-Benz', 'modelo': 'Clase A', 'cilindrada': 2.0, 'anio': 2022},
            {'marca': 'Mercedes-Benz', 'modelo': 'Clase C', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'Mercedes-Benz', 'modelo': 'Clase C', 'cilindrada': 2.0, 'anio': 2023},
            {'marca': 'Mercedes-Benz', 'modelo': 'Clase E', 'cilindrada': 3.0, 'anio': 2022},
            {'marca': 'Mercedes-Benz', 'modelo': 'AMG GT', 'cilindrada': 4.0, 'anio': 2022},
            {'marca': 'Mercedes-Benz', 'modelo': 'GLC', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'Mercedes-Benz', 'modelo': 'GLE', 'cilindrada': 3.0, 'anio': 2023},
            {'marca': 'Mercedes-Benz', 'modelo': 'AMG C63', 'cilindrada': 4.0, 'anio': 2022},
            
            # Porsche
            {'marca': 'Porsche', 'modelo': '911 Carrera', 'cilindrada': 3.0, 'anio': 2021},
            {'marca': 'Porsche', 'modelo': '911 Carrera S', 'cilindrada': 3.0, 'anio': 2022},
            {'marca': 'Porsche', 'modelo': '911 Turbo', 'cilindrada': 3.8, 'anio': 2023},
            {'marca': 'Porsche', 'modelo': 'Cayenne', 'cilindrada': 3.0, 'anio': 2021},
            {'marca': 'Porsche', 'modelo': 'Cayenne S', 'cilindrada': 4.0, 'anio': 2022},
            {'marca': 'Porsche', 'modelo': 'Macan', 'cilindrada': 2.0, 'anio': 2022},
            {'marca': 'Porsche', 'modelo': 'Panamera', 'cilindrada': 2.9, 'anio': 2021},
            {'marca': 'Porsche', 'modelo': 'Taycan', 'cilindrada': 0.0, 'anio': 2023},
            
            # Volkswagen
            {'marca': 'Volkswagen', 'modelo': 'Golf GTI', 'cilindrada': 2.0, 'anio': 2020},
            {'marca': 'Volkswagen', 'modelo': 'Golf GTI', 'cilindrada': 2.0, 'anio': 2022},
            {'marca': 'Volkswagen', 'modelo': 'Golf R', 'cilindrada': 2.0, 'anio': 2022},
            {'marca': 'Volkswagen', 'modelo': 'Passat', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'Volkswagen', 'modelo': 'Tiguan', 'cilindrada': 2.0, 'anio': 2021},
            {'marca': 'Volkswagen', 'modelo': 'Arteon', 'cilindrada': 2.0, 'anio': 2022},
            {'marca': 'Volkswagen', 'modelo': 'Jetta GLI', 'cilindrada': 2.0, 'anio': 2021},
        ]

        # Crear vehículos
        vehiculos_creados = []
        for veh_data in vehiculos_data:
            veh, created = vehiculo.objects.get_or_create(
                marca=veh_data['marca'],
                modelo=veh_data['modelo'],
                cilindrada=veh_data['cilindrada'],
                anio=veh_data['anio']
            )
            vehiculos_creados.append(veh)
            status = 'CREADO' if created else 'YA EXISTE'
            self.stdout.write(f'  [{status}] {veh}')

        self.stdout.write(self.style.SUCCESS(f'\n✓ {len(vehiculos_creados)} vehículos procesados\n'))

        # ==================== ASOCIACIONES PRODUCTO-VEHÍCULO ====================
        # Mapeo de qué llantas van con qué vehículos (basado en apernadura y medidas)
        
        # 5x112 - Audi, VW, Mercedes
        llantas_5x112 = [p for p in productos_creados if p.apernadura == '5x112']
        vehiculos_5x112 = [v for v in vehiculos_creados if v.marca in ['Audi', 'Volkswagen', 'Mercedes-Benz']]
        
        # 5x120 - BMW
        llantas_5x120 = [p for p in productos_creados if p.apernadura == '5x120']
        vehiculos_5x120 = [v for v in vehiculos_creados if v.marca == 'BMW']
        
        # 5x130 - Porsche
        llantas_5x130 = [p for p in productos_creados if p.apernadura == '5x130']
        vehiculos_5x130 = [v for v in vehiculos_creados if v.marca == 'Porsche']
        
        # 5x100 - VW (algunos modelos antiguos)
        llantas_5x100 = [p for p in productos_creados if p.apernadura == '5x100']
        vehiculos_5x100 = [v for v in vehiculos_creados if v.marca == 'Volkswagen' and 'Golf' in v.modelo]

        asociaciones_creadas = 0
        
        # Crear asociaciones 5x112
        for llanta in llantas_5x112:
            for veh in vehiculos_5x112:
                _, created = Producto_Vehiculo.objects.get_or_create(
                    producto=llanta,
                    vehiculo=veh
                )
                if created:
                    asociaciones_creadas += 1

        # Crear asociaciones 5x120
        for llanta in llantas_5x120:
            for veh in vehiculos_5x120:
                _, created = Producto_Vehiculo.objects.get_or_create(
                    producto=llanta,
                    vehiculo=veh
                )
                if created:
                    asociaciones_creadas += 1

        # Crear asociaciones 5x130
        for llanta in llantas_5x130:
            for veh in vehiculos_5x130:
                _, created = Producto_Vehiculo.objects.get_or_create(
                    producto=llanta,
                    vehiculo=veh
                )
                if created:
                    asociaciones_creadas += 1

        # Crear asociaciones 5x100
        for llanta in llantas_5x100:
            for veh in vehiculos_5x100:
                _, created = Producto_Vehiculo.objects.get_or_create(
                    producto=llanta,
                    vehiculo=veh
                )
                if created:
                    asociaciones_creadas += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {asociaciones_creadas} asociaciones producto-vehículo creadas\n'))

        # ==================== RESUMEN ====================
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('RESUMEN FINAL:'))
        self.stdout.write(f'  • Productos en BD: {Producto.objects.count()}')
        self.stdout.write(f'  • Vehículos en BD: {vehiculo.objects.count()}')
        self.stdout.write(f'  • Asociaciones en BD: {Producto_Vehiculo.objects.count()}')
        self.stdout.write('='*50 + '\n')
        
        self.stdout.write(self.style.SUCCESS('¡Datos poblados exitosamente!'))
