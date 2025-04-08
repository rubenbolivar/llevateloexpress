// Datos de productos
window.products = [
    {
        id: 1,
        name: "Voge Rally 300",
        category: "motocicletas",
        brand: "Voge",
        price: 4500,
        image: "img/products/300.jpg",
        description: "La Voge Rally 300 es una motocicleta de aventura ligera que combina versatilidad y rendimiento. Perfecta para quienes buscan una moto capaz tanto en ciudad como en caminos de tierra.",
        features: [
            "Motor monocilíndrico de 292cc refrigerado por líquido",
            "Potencia máxima de 29 HP a 8500 rpm",
            "Transmisión de 6 velocidades",
            "Frenos de disco con ABS desconectable",
            "Suspensión invertida ajustable",
            "Panel de instrumentos TFT a color",
            "Iluminación full LED",
            "Capacidad de tanque: 16 litros"
        ],
        specs: {
            general: [
                { label: 'Marca', value: 'Voge' },
                { label: 'Modelo', value: 'Rally 300' },
                { label: 'Año', value: '2023' },
                { label: 'Tipo', value: 'Adventure' },
                { label: 'País de Origen', value: 'China' },
                { label: 'Garantía', value: '2 años o 20,000 km' },
                { label: 'Colores disponibles', value: 'Negro, Rojo, Gris' },
                { label: 'Peso', value: '178 kg' }
            ],
            engine: [
                { label: 'Tipo de motor', value: 'Monocilíndrico 4T, DOHC, 4 válvulas' },
                { label: 'Cilindrada', value: '292 cc' },
                { label: 'Potencia máxima', value: '29 HP a 8500 rpm' },
                { label: 'Torque máximo', value: '25.3 Nm a 6500 rpm' },
                { label: 'Transmisión', value: '6 velocidades' },
                { label: 'Sistema de refrigeración', value: 'Líquido' },
                { label: 'Capacidad de tanque', value: '16 litros' },
                { label: 'Consumo promedio', value: '3.3 L/100km' }
            ],
            comfort: [
                { label: 'Asiento', value: 'Doble altura, ergonómico' },
                { label: 'Altura del asiento', value: '825 mm' },
                { label: 'Panel de instrumentos', value: 'TFT a color de 5"' },
                { label: 'Iluminación', value: 'Full LED' },
                { label: 'USB', value: 'Sí, puerto cargador 2.1A' },
                { label: 'Posición de manejo', value: 'Adventure, semi-erguida' },
                { label: 'Capacidad de carga', value: '12 kg' },
                { label: 'Parabrisas', value: 'Ajustable 3 posiciones' }
            ],
            safety: [
                { label: 'Freno delantero', value: 'Disco 300mm, pinza de 4 pistones, ABS' },
                { label: 'Freno trasero', value: 'Disco 240mm, pinza de 1 pistón, ABS' },
                { label: 'Sistema de frenos', value: 'Hidráulico, doble disco, ABS desconectable' },
                { label: 'ABS', value: 'Bosch 9.1 MB, desconectable' },
                { label: 'Control de tracción', value: 'No disponible' },
                { label: 'Suspensión delantera', value: 'Horquilla invertida 41mm, ajustable' },
                { label: 'Suspensión trasera', value: 'Monoamortiguador con depósito separado' },
                { label: 'Tipo de suspensión', value: 'Invertida delantera, monoamortiguador trasero' },
                { label: 'Recorrido suspensiones', value: '160mm delantero / 150mm trasero' },
                { label: 'Neumático delantero', value: '100/90-19' },
                { label: 'Neumático trasero', value: '140/80-17' },
                { label: 'Tamaño de ruedas', value: '19" delantera, 17" trasera' }
            ]
        },
        stock: 8,
        featured: true
    },
    {
        id: 2,
        name: "Voge 525 DSX",
        category: "motocicletas",
        brand: "Voge",
        price: 6800,
        image: "img/products/525dsx.jpg",
        description: "La Voge 525 DSX es una motocicleta trail de media cilindrada que ofrece excelentes prestaciones para aventuras on/off-road. Su diseño moderno y equipamiento premium la hacen destacar en su segmento.",
        features: [
            "Motor bicilíndrico en línea de 494cc",
            "Potencia de 46.2 HP a 8500 rpm",
            "Transmisión de 6 velocidades",
            "Sistema de frenos ABS Bosch de doble canal",
            "Suspensión KYB totalmente ajustable",
            "Pantalla TFT de 7 pulgadas",
            "Modos de conducción",
            "Control de tracción"
        ],
        specs: {
            general: [
                { label: 'Marca', value: 'Voge' },
                { label: 'Modelo', value: '525 DSX' },
                { label: 'Año', value: '2023' },
                { label: 'Tipo', value: 'Trail Adventure' },
                { label: 'País de Origen', value: 'China' },
                { label: 'Garantía', value: '2 años o 20,000 km' },
                { label: 'Colores disponibles', value: 'Negro, Azul, Gris mate' },
                { label: 'Peso', value: '205 kg' }
            ],
            engine: [
                { label: 'Tipo de motor', value: 'Bicilíndrico en línea, 4T, DOHC, 8 válvulas' },
                { label: 'Cilindrada', value: '494 cc' },
                { label: 'Potencia máxima', value: '46.2 HP a 8500 rpm' },
                { label: 'Torque máximo', value: '45 Nm a 7000 rpm' },
                { label: 'Transmisión', value: '6 velocidades' },
                { label: 'Sistema de refrigeración', value: 'Líquido' },
                { label: 'Capacidad de tanque', value: '19 litros' },
                { label: 'Consumo promedio', value: '4.1 L/100km' }
            ],
            comfort: [
                { label: 'Asiento', value: 'Ergonómico, tapizado antideslizante' },
                { label: 'Altura del asiento', value: '840 mm' },
                { label: 'Panel de instrumentos', value: 'TFT a color de 7 pulgadas' },
                { label: 'Iluminación', value: 'Full LED con DRL' },
                { label: 'USB', value: 'Sí, puerto cargador tipo C' },
                { label: 'Posición de manejo', value: 'Adventure/Touring' },
                { label: 'Capacidad de carga', value: '18 kg' },
                { label: 'Parabrisas', value: 'Regulable en altura' }
            ],
            safety: [
                { label: 'Freno delantero', value: 'Doble disco 320mm, pinzas radiales de 4 pistones' },
                { label: 'Freno trasero', value: 'Disco 260mm, pinza flotante de 2 pistones' },
                { label: 'Sistema de frenos', value: 'Hidráulico, doble disco delantero, ABS en ambos ejes' },
                { label: 'ABS', value: 'Bosch 9.1 MB, modos Road/Off-road' },
                { label: 'Control de tracción', value: 'Sí, desconectable, 2 modos' },
                { label: 'Suspensión delantera', value: 'KYB invertida de 43mm, totalmente ajustable' },
                { label: 'Suspensión trasera', value: 'KYB monoamortiguador con depósito separado' },
                { label: 'Tipo de suspensión', value: 'Invertida delantera, monoamortiguador trasero, ambas ajustables' },
                { label: 'Recorrido suspensiones', value: '170mm delantero / 175mm trasero' },
                { label: 'Neumático delantero', value: '110/80-R19' },
                { label: 'Neumático trasero', value: '150/70-R17' },
                { label: 'Tamaño de ruedas', value: '19" delantera, 17" trasera' }
            ]
        },
        stock: 5,
        featured: true
    },
    {
        id: 3,
        name: "Voge AC 525 X",
        category: "motocicletas",
        brand: "Voge",
        price: 7200,
        image: "img/products/ac525.jpg",
        description: "La Voge AC 525 X representa la evolución en el segmento adventure touring. Con su diseño sofisticado y tecnología avanzada, ofrece el equilibrio perfecto entre confort y capacidad todoterreno.",
        features: [
            "Motor bicilíndrico de 494cc refrigerado por líquido",
            "48 HP de potencia máxima",
            "Transmisión de 6 velocidades con embrague anti-rebote",
            "Sistema de frenos ABS Bosch con modo off-road",
            "Suspensión KYB con recorrido extendido",
            "Pantalla TFT con conectividad bluetooth",
            "Control de crucero",
            "Protectores de motor y manos incluidos"
        ],
        specs: {
            general: [
                { label: 'Marca', value: 'Voge' },
                { label: 'Modelo', value: 'AC 525 X' },
                { label: 'Año', value: '2023' },
                { label: 'Tipo', value: 'Adventure Touring' },
                { label: 'País de Origen', value: 'China' },
                { label: 'Garantía', value: '2 años o 20,000 km' },
                { label: 'Colores disponibles', value: 'Negro, Rojo Rally, Azul' },
                { label: 'Peso', value: '215 kg' }
            ],
            engine: [
                { label: 'Tipo de motor', value: 'Bicilíndrico en línea, 4T, DOHC, 8 válvulas' },
                { label: 'Cilindrada', value: '494 cc' },
                { label: 'Potencia máxima', value: '48 HP a 8750 rpm' },
                { label: 'Torque máximo', value: '47 Nm a 7000 rpm' },
                { label: 'Transmisión', value: '6 velocidades con embrague anti-rebote' },
                { label: 'Sistema de refrigeración', value: 'Líquido' },
                { label: 'Capacidad de tanque', value: '21 litros' },
                { label: 'Consumo promedio', value: '4.3 L/100km' }
            ],
            comfort: [
                { label: 'Asiento', value: 'Touring, altura ajustable 830-850 mm' },
                { label: 'Altura del asiento', value: '830-850 mm (ajustable)' },
                { label: 'Panel de instrumentos', value: 'TFT a color de 7" con conectividad bluetooth' },
                { label: 'Iluminación', value: 'Full LED con iluminación adaptativa en curvas' },
                { label: 'USB', value: 'Sí, dos puertos (tipo A y tipo C)' },
                { label: 'Posición de manejo', value: 'Touring, protegida del viento' },
                { label: 'Capacidad de carga', value: '25 kg' },
                { label: 'Parabrisas', value: 'Regulable en altura y ángulo' }
            ],
            safety: [
                { label: 'Freno delantero', value: 'Doble disco 320mm, pinzas Brembo monobloque de 4 pistones' },
                { label: 'Freno trasero', value: 'Disco 260mm, pinza Brembo de 2 pistones' },
                { label: 'Sistema de frenos', value: 'Hidráulico, Brembo, doble disco delantero, ABS de triple modo' },
                { label: 'ABS', value: 'Bosch 9.3 MP, modos Road/Off-road/Desconectable' },
                { label: 'Control de tracción', value: 'Sí, 3 modos + desconectable' },
                { label: 'Suspensión delantera', value: 'KYB invertida de 43mm, totalmente ajustable, 170mm recorrido' },
                { label: 'Suspensión trasera', value: 'KYB monoamortiguador con depósito separado, 180mm recorrido' },
                { label: 'Tipo de suspensión', value: 'Invertida delantera, monoamortiguador trasero, ambas ajustables' },
                { label: 'Recorrido suspensiones', value: '170mm delantero / 180mm trasero' },
                { label: 'Neumático delantero', value: '120/70-R19' },
                { label: 'Neumático trasero', value: '170/60-R17' },
                { label: 'Tamaño de ruedas', value: '19" delantera, 17" trasera' }
            ]
        },
        stock: 6,
        featured: true
    },
    {
        id: 4,
        name: "Suzuki DR 650",
        category: "motocicletas",
        brand: "Suzuki",
        price: 8500,
        image: "img/products/dr650.jpg",
        description: "La legendaria Suzuki DR 650 es sinónimo de confiabilidad y versatilidad. Una moto dual-purpose que ha probado su valor tanto en largas travesías como en el uso diario.",
        features: [
            "Motor monocilíndrico SOHC de 644cc refrigerado por aire",
            "Potencia de 46 HP",
            "Transmisión de 5 velocidades",
            "Freno de disco delantero y trasero",
            "Suspensión de largo recorrido",
            "Altura de asiento ajustable",
            "Peso en seco de 166 kg",
            "Tanque de combustible de 13 litros"
        ],
        specs: {
            general: [
                { label: 'Marca', value: 'Suzuki' },
                { label: 'Modelo', value: 'DR 650' },
                { label: 'Año', value: '2023' },
                { label: 'Tipo', value: 'Dual Purpose' },
                { label: 'País de Origen', value: 'Japón' },
                { label: 'Garantía', value: '1 año sin límite de kilometraje' },
                { label: 'Colores disponibles', value: 'Blanco, Negro' },
                { label: 'Peso', value: '166 kg (seco)' }
            ],
            engine: [
                { label: 'Tipo de motor', value: 'Monocilíndrico SOHC, 4T, 4 válvulas' },
                { label: 'Cilindrada', value: '644 cc' },
                { label: 'Potencia máxima', value: '46 HP a 6400 rpm' },
                { label: 'Torque máximo', value: '58 Nm a 5000 rpm' },
                { label: 'Transmisión', value: '5 velocidades' },
                { label: 'Sistema de refrigeración', value: 'Aire/aceite' },
                { label: 'Capacidad de tanque', value: '13 litros' },
                { label: 'Consumo promedio', value: '4.5 L/100km' }
            ],
            comfort: [
                { label: 'Asiento', value: 'Altura ajustable 840-870 mm' },
                { label: 'Altura del asiento', value: '840-870 mm (ajustable)' },
                { label: 'Panel de instrumentos', value: 'Analógico' },
                { label: 'Iluminación', value: 'Halógena' },
                { label: 'USB', value: 'No disponible de serie' },
                { label: 'Posición de manejo', value: 'Erguida, off-road' },
                { label: 'Capacidad de carga', value: '20 kg' },
                { label: 'Parabrisas', value: 'No incluido de serie' }
            ],
            safety: [
                { label: 'Freno delantero', value: 'Disco 290mm, pinza de 2 pistones' },
                { label: 'Freno trasero', value: 'Disco 240mm, pinza de 1 pistón' },
                { label: 'Sistema de frenos', value: 'Hidráulico, disco simple en ambos ejes, sin ABS' },
                { label: 'ABS', value: 'No disponible' },
                { label: 'Control de tracción', value: 'No disponible' },
                { label: 'Suspensión delantera', value: 'Telescópica convencional, 260mm recorrido' },
                { label: 'Suspensión trasera', value: 'Monoamortiguador con sistema de bieletas, 280mm recorrido' },
                { label: 'Tipo de suspensión', value: 'Convencional delantera, monoamortiguador trasero' },
                { label: 'Recorrido suspensiones', value: '260mm delantero / 280mm trasero' },
                { label: 'Neumático delantero', value: '90/90-21' },
                { label: 'Neumático trasero', value: '120/90-17' },
                { label: 'Tamaño de ruedas', value: '21" delantera, 17" trasera' }
            ]
        },
        stock: 4,
        featured: true
    },
    {
        id: 5,
        name: "Suzuki GN 125",
        category: "motocicletas",
        brand: "Suzuki",
        price: 2200,
        image: "img/products/gn125.jpg",
        description: "La Suzuki GN 125 es una motocicleta clásica ideal para principiantes y uso urbano. Su diseño atemporal, bajo consumo y fácil mantenimiento la han convertido en un referente de su categoría.",
        features: [
            "Motor monocilíndrico de 124cc refrigerado por aire",
            "Potencia de 12.5 HP a 9500 rpm",
            "Transmisión de 5 velocidades",
            "Freno de disco delantero y tambor trasero",
            "Arranque eléctrico y por patada",
            "Consumo aproximado de 2.2L/100km",
            "Peso en orden de marcha: 113 kg",
            "Capacidad de tanque: 10.5 litros"
        ],
        specs: {
            general: [
                { label: 'Marca', value: 'Suzuki' },
                { label: 'Modelo', value: 'GN 125' },
                { label: 'Año', value: '2023' },
                { label: 'Tipo', value: 'Street / Commuter' },
                { label: 'País de Origen', value: 'Japón' },
                { label: 'Garantía', value: '1 año sin límite de kilometraje' },
                { label: 'Colores disponibles', value: 'Negro, Rojo, Azul' },
                { label: 'Peso', value: '113 kg' }
            ],
            engine: [
                { label: 'Tipo de motor', value: 'Monocilíndrico, 4T, SOHC, 2 válvulas' },
                { label: 'Cilindrada', value: '124 cc' },
                { label: 'Potencia máxima', value: '12.5 HP a 9500 rpm' },
                { label: 'Torque máximo', value: '9.8 Nm a 8000 rpm' },
                { label: 'Transmisión', value: '5 velocidades' },
                { label: 'Sistema de refrigeración', value: 'Aire' },
                { label: 'Capacidad de tanque', value: '10.5 litros' },
                { label: 'Consumo promedio', value: '2.2 L/100km' }
            ],
            comfort: [
                { label: 'Asiento', value: 'Biplaza, estilo clásico' },
                { label: 'Altura del asiento', value: '770 mm' },
                { label: 'Panel de instrumentos', value: 'Analógico, velocímetro y tacómetro' },
                { label: 'Iluminación', value: 'Halógena' },
                { label: 'USB', value: 'No disponible de serie' },
                { label: 'Posición de manejo', value: 'Erguida, urbana' },
                { label: 'Capacidad de carga', value: '10 kg' },
                { label: 'Parabrisas', value: 'No incluido' }
            ],
            safety: [
                { label: 'Freno delantero', value: 'Disco 240mm, pinza de 2 pistones' },
                { label: 'Freno trasero', value: 'Tambor 130mm' },
                { label: 'Sistema de frenos', value: 'Hidráulico delantero, mecánico trasero' },
                { label: 'ABS', value: 'No disponible' },
                { label: 'Control de tracción', value: 'No disponible' },
                { label: 'Suspensión delantera', value: 'Horquilla telescópica convencional' },
                { label: 'Suspensión trasera', value: 'Doble amortiguador con precarga ajustable' },
                { label: 'Tipo de suspensión', value: 'Convencional delantera, doble amortiguador trasero' },
                { label: 'Recorrido suspensiones', value: '120mm delantero / 95mm trasero' },
                { label: 'Neumático delantero', value: '2.75-18' },
                { label: 'Neumático trasero', value: '3.50-16' },
                { label: 'Tamaño de ruedas', value: '18" delantera, 16" trasera' }
            ]
        },
        stock: 12,
        featured: true
    },
    {
        id: 6,
        name: "Voge SR4",
        category: "motocicletas",
        brand: "Voge",
        price: 5500,
        image: "img/products/sr4.jpg",
        description: "La Voge SR4 es una motocicleta deportiva que combina estilo y rendimiento. Su diseño moderno y tecnología avanzada la convierten en una opción atractiva para los amantes de las motos deportivas.",
        features: [
            "Motor bicilíndrico en línea de 350cc",
            "Potencia de 42.5 HP a 9000 rpm",
            "Transmisión de 6 velocidades",
            "Sistema de frenos ABS de doble canal",
            "Suspensión invertida ajustable",
            "Pantalla TFT a color",
            "Iluminación full LED",
            "Modos de conducción seleccionables"
        ],
        specs: {
            general: [
                { label: 'Marca', value: 'Voge' },
                { label: 'Modelo', value: 'SR4' },
                { label: 'Año', value: '2023' },
                { label: 'Tipo', value: 'Sport' },
                { label: 'País de Origen', value: 'China' },
                { label: 'Garantía', value: '2 años o 20,000 km' },
                { label: 'Colores disponibles', value: 'Negro, Rojo, Blanco' },
                { label: 'Peso', value: '185 kg' }
            ],
            engine: [
                { label: 'Tipo de motor', value: 'Bicilíndrico en línea, 4T, DOHC, 8 válvulas' },
                { label: 'Cilindrada', value: '350 cc' },
                { label: 'Potencia máxima', value: '42.5 HP a 9000 rpm' },
                { label: 'Torque máximo', value: '35 Nm a 7500 rpm' },
                { label: 'Transmisión', value: '6 velocidades' },
                { label: 'Sistema de refrigeración', value: 'Líquido' },
                { label: 'Capacidad de tanque', value: '15 litros' },
                { label: 'Consumo promedio', value: '3.8 L/100km' }
            ],
            comfort: [
                { label: 'Asiento', value: 'Deportivo biplaza' },
                { label: 'Altura del asiento', value: '810 mm' },
                { label: 'Panel de instrumentos', value: 'TFT a color de 5"' },
                { label: 'Iluminación', value: 'Full LED' },
                { label: 'USB', value: 'Sí, puerto cargador tipo C' },
                { label: 'Posición de manejo', value: 'Deportiva, semi-inclinada' },
                { label: 'Capacidad de carga', value: '8 kg' },
                { label: 'Parabrisas', value: 'Deportivo aerodinámico' }
            ],
            safety: [
                { label: 'Freno delantero', value: 'Doble disco 300mm, pinzas radiales de 4 pistones' },
                { label: 'Freno trasero', value: 'Disco 240mm, pinza flotante de 1 pistón' },
                { label: 'Sistema de frenos', value: 'Hidráulico, doble disco delantero, ABS en ambos ejes' },
                { label: 'ABS', value: 'Bosch 9.1 MB, doble canal' },
                { label: 'Control de tracción', value: 'Sí, 2 modos + desconectable' },
                { label: 'Suspensión delantera', value: 'Horquilla invertida de 41mm, ajustable' },
                { label: 'Suspensión trasera', value: 'Monoamortiguador ajustable en precarga' },
                { label: 'Tipo de suspensión', value: 'Invertida delantera, monoamortiguador trasero' },
                { label: 'Recorrido suspensiones', value: '140mm delantero / 130mm trasero' },
                { label: 'Neumático delantero', value: '120/70-ZR17' },
                { label: 'Neumático trasero', value: '160/60-ZR17' },
                { label: 'Tamaño de ruedas', value: '17" delantera, 17" trasera' }
            ]
        },
        stock: 7,
        featured: true
    },
    {
        id: 7,
        name: "Suzuki V-Strom 250",
        category: "motocicletas",
        brand: "Suzuki",
        price: 5800,
        image: "img/products/vstrom.jpg",
        description: "La Suzuki V-Strom 250 es una aventurera ligera que hereda el ADN de la familia V-Strom. Perfecta para iniciarse en el mundo adventure, ofrece comodidad y versatilidad en un paquete accesible.",
        features: [
            "Motor bicilíndrico paralelo de 248cc",
            "Potencia de 25 HP a 8000 rpm",
            "Transmisión de 6 velocidades",
            "Sistema ABS de serie",
            "Suspensión telescópica delantera",
            "Panel LCD multifunción",
            "Parabrisas ajustable",
            "Capacidad de tanque: 17.3 litros"
        ],
        specs: {
            general: [
                { label: 'Marca', value: 'Suzuki' },
                { label: 'Modelo', value: 'V-Strom 250' },
                { label: 'Año', value: '2023' },
                { label: 'Tipo', value: 'Adventure' },
                { label: 'País de Origen', value: 'Japón' },
                { label: 'Garantía', value: '2 años o 24,000 km' },
                { label: 'Colores disponibles', value: 'Amarillo, Negro, Gris' },
                { label: 'Peso', value: '188 kg' }
            ],
            engine: [
                { label: 'Tipo de motor', value: 'Bicilíndrico paralelo, 4T, SOHC, 4 válvulas' },
                { label: 'Cilindrada', value: '248 cc' },
                { label: 'Potencia máxima', value: '25 HP a 8000 rpm' },
                { label: 'Torque máximo', value: '23.4 Nm a 6500 rpm' },
                { label: 'Transmisión', value: '6 velocidades' },
                { label: 'Sistema de refrigeración', value: 'Líquido' },
                { label: 'Capacidad de tanque', value: '17.3 litros' },
                { label: 'Consumo promedio', value: '3.1 L/100km' }
            ],
            comfort: [
                { label: 'Asiento', value: 'Biplaza escalonado' },
                { label: 'Altura del asiento', value: '800 mm' },
                { label: 'Panel de instrumentos', value: 'LCD multifunción' },
                { label: 'Iluminación', value: 'LED (posición) y halógena (principal)' },
                { label: 'USB', value: 'Sí, puerto cargador' },
                { label: 'Posición de manejo', value: 'Erguida, confortable' },
                { label: 'Capacidad de carga', value: '15 kg' },
                { label: 'Parabrisas', value: 'Ajustable en 3 posiciones' }
            ],
            safety: [
                { label: 'Freno delantero', value: 'Disco 290mm, pinza de 2 pistones' },
                { label: 'Freno trasero', value: 'Disco 240mm, pinza de 1 pistón' },
                { label: 'Sistema de frenos', value: 'Hidráulico, disco simple en ambos ejes, ABS' },
                { label: 'ABS', value: 'Bosch, doble canal' },
                { label: 'Control de tracción', value: 'No disponible' },
                { label: 'Suspensión delantera', value: 'Horquilla telescópica convencional, 120mm recorrido' },
                { label: 'Suspensión trasera', value: 'Monoamortiguador con sistema de bieletas, 125mm recorrido' },
                { label: 'Tipo de suspensión', value: 'Convencional delantera, monoamortiguador trasero' },
                { label: 'Recorrido suspensiones', value: '120mm delantero / 125mm trasero' },
                { label: 'Neumático delantero', value: '110/80-17' },
                { label: 'Neumático trasero', value: '140/70-17' },
                { label: 'Tamaño de ruedas', value: '17" delantera, 17" trasera' }
            ]
        },
        stock: 9,
        featured: true
    }
];

// Asignar a una variable global normal para compatibilidad con el código existente
const products = window.products;

// Cargar productos destacados en la página principal
document.addEventListener('DOMContentLoaded', function() {
    console.log('[products.js] DOM cargado, productos disponibles:', window.products.length);
    
    const featuredContainer = document.getElementById('featured-products-container');
    
    if(featuredContainer) {
        console.log('[products.js] Cargando productos destacados');
        // Filtrar productos destacados
        const featuredProducts = window.products.filter(product => product.featured);
        
        // Generar HTML para cada producto
        featuredProducts.forEach(product => {
            const productCard = createProductCard(product);
            featuredContainer.appendChild(productCard);
        });
        
        // Configurar filtros
        setupFilters();
    }
});

// Crear tarjeta de producto
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'col-md-4 mb-4 product-card';
    card.dataset.category = product.category;
    card.dataset.brand = product.brand;
    card.dataset.price = product.price;
    
    card.innerHTML = `
        <div class="card h-100 border-0 shadow-sm">
            <div class="position-relative">
                <img src="${product.image || 'img/products/placeholder.jpg'}" class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">
                <div class="position-absolute top-0 start-0 m-3">
                    <span class="badge bg-primary">${getCategoryName(product.category)}</span>
                </div>
            </div>
            <div class="card-body d-flex flex-column">
                <h5 class="card-title">${product.name}</h5>
                <p class="card-text text-muted small mb-0">Marca: ${product.brand}</p>
                <p class="card-text text-primary fw-bold mt-2 mb-3">$${product.price.toLocaleString()}</p>
                <p class="card-text">${product.description.slice(0, 80)}...</p>
                <div class="mt-auto d-flex justify-content-between">
                    <a href="detalle-producto.html?id=${product.id}" class="btn btn-outline-secondary btn-sm">
                        <i class="fas fa-eye me-1"></i>Ver detalles
                    </a>
                    <a href="calculadora.html?modelo=${product.id}" class="btn btn-primary btn-sm">
                        <i class="fas fa-calculator me-1"></i>Financiar
                    </a>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Obtener nombre legible de categoría
function getCategoryName(category) {
    const categories = {
        'motocicletas': 'Motocicleta',
        'vehiculos': 'Vehículo',
        'maquinaria': 'Maquinaria Agrícola',
        'camiones': 'Camión',
        'equipos': 'Maquinaria y Equipos'
    };
    
    return categories[category] || category;
}

// Configurar filtros
function setupFilters() {
    // Filtro de categoría
    const categoryFilter = document.getElementById('categoryFilter');
    if(categoryFilter) {
        const categoryMenu = categoryFilter.nextElementSibling;
        const categoryOptions = categoryMenu.querySelectorAll('.dropdown-item');
        
        categoryOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedCategory = this.textContent.toLowerCase();
                filterProducts('category', selectedCategory);
                categoryFilter.textContent = this.textContent;
            });
        });
    }
    
    // Filtro de marca
    const brandFilter = document.getElementById('brandFilter');
    if(brandFilter) {
        const brandMenu = brandFilter.nextElementSibling;
        const brandOptions = brandMenu.querySelectorAll('.dropdown-item');
        
        brandOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedBrand = this.textContent;
                filterProducts('brand', selectedBrand);
                brandFilter.textContent = this.textContent;
            });
        });
    }
    
    // Filtro de precio
    const priceFilter = document.getElementById('priceFilter');
    if(priceFilter) {
        const priceMenu = priceFilter.nextElementSibling;
        const priceOptions = priceMenu.querySelectorAll('.dropdown-item');
        
        priceOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedPrice = this.textContent;
                
                const container = document.getElementById('featured-products-container');
                const cards = Array.from(container.querySelectorAll('.product-card'));
                
                if(selectedPrice === 'Menor precio') {
                    cards.sort((a, b) => parseInt(a.dataset.price) - parseInt(b.dataset.price));
                } else {
                    cards.sort((a, b) => parseInt(b.dataset.price) - parseInt(a.dataset.price));
                }
                
                container.innerHTML = '';
                cards.forEach(card => container.appendChild(card));
                
                priceFilter.textContent = this.textContent;
            });
        });
    }
}

// Filtrar productos
function filterProducts(filterType, filterValue) {
    const container = document.getElementById('featured-products-container');
    const cards = container.querySelectorAll('.product-card');
    
    cards.forEach(card => {
        if(filterValue === 'todos' || filterValue === 'todas') {
            card.style.display = 'block';
        } else {
            if(filterType === 'category') {
                const category = card.dataset.category;
                
                if(filterValue === 'motocicletas' && category === 'motocicletas') {
                    card.style.display = 'block';
                } else if(filterValue === 'vehículos' && category === 'vehiculos') {
                    card.style.display = 'block';
                } else if(filterValue === 'maquinaria' && category === 'maquinaria') {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            } else if(filterType === 'brand') {
                const brand = card.dataset.brand;
                card.style.display = (brand === filterValue) ? 'block' : 'none';
            }
        }
    });
} 