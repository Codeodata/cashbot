FROM public.ecr.aws/lambda/python:3.13

# Copiar requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Configurar Python path
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/src"

# Handler de Lambda
CMD ["src.app.main.lambda_handler"]
