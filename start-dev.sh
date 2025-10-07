#!/bin/bash

# Script para levantar servicios de desarrollo
echo "🚀 Levantando servicios de desarrollo..."

# Levantar PostgreSQL y Redis con Docker Compose
echo "📦 Levantando PostgreSQL y Redis..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar que PostgreSQL esté funcionando
echo "🔍 Verificando PostgreSQL..."
docker-compose exec postgres pg_isready -U postgres

# Verificar que Redis esté funcionando
echo "🔍 Verificando Redis..."
docker-compose exec redis redis-cli ping

echo "✅ Servicios listos!"
echo "📊 PostgreSQL: localhost:5432"
echo "🔴 Redis: localhost:6379"
echo ""
echo "Para ejecutar la API:"
echo "cd saas3d/api"
echo "python -m venv venv"
echo "source venv/bin/activate  # Windows: venv\\Scripts\\activate"
echo "pip install -r requirements.txt"
echo "uvicorn main:app --reload"
