# Guía de Contribución

¡Gracias por tu interés en contribuir a BIMView SaaS! 🚀

## Cómo Contribuir

### 1. Fork y Clone
```bash
git clone https://github.com/tu-usuario/BIMView-SaaS.git
cd BIMView-SaaS
```

### 2. Crear una rama
```bash
git checkout -b feature/nueva-caracteristica
```

### 3. Instalar dependencias
```bash
# Backend
cd saas3d/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 4. Hacer cambios
- Sigue las convenciones de código
- Añade tests para nuevas funcionalidades
- Actualiza documentación si es necesario

### 5. Ejecutar tests
```bash
# Backend tests
cd saas3d/api
pytest

# Frontend tests
cd ../frontend
npm test
```

### 6. Commit y Push
```bash
git add .
git commit -m "feat: añadir nueva característica"
git push origin feature/nueva-caracteristica
```

### 7. Crear Pull Request
- Ve a GitHub y crea un Pull Request
- Completa el template de PR
- Espera la revisión del código

## Convenciones

### Commits
Usa [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` nueva característica
- `fix:` corrección de bug
- `docs:` cambios en documentación
- `style:` formato, punto y coma faltante, etc.
- `refactor:` refactorización de código
- `test:` añadir tests
- `chore:` cambios en build, dependencias, etc.

### Código
- **Python**: PEP 8, type hints
- **TypeScript**: ESLint configurado
- **Tests**: Cobertura mínima del 80%

## Reportar Bugs

Usa el template de bug report en GitHub Issues.

## Solicitar Características

Usa el template de feature request en GitHub Issues.

## Preguntas

- Abre un issue con la etiqueta `question`
- Únete a nuestras discusiones

¡Gracias por contribuir! 🎉
