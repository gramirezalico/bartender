# servicePrint (Flask)

API mínima en Flask con **un solo endpoint** para recibir JSON y guardarlo como CSV en una ruta local o UNC (por ejemplo `//10.100.2.54/SELLADOBIXOLON_TI$/EtiquetaTep.CSV`).

## 1) Instalar dependencias

```bash
pip install -r requirements.txt
```

## 2) Ejecutar

```bash
python app.py
```

Servidor en `http://localhost:5000`.

## 3) Endpoint único

`POST /csv`

### Body esperado

```json
{
  "destination": "//10.100.2.54/SELLADOBIXOLON_TI$/EtiquetaTep.CSV",
  "columns": [
    "Job",
    "Part",
    "Desc",
    "EMP",
    "Pa",
    "OP",
    "Cantidad",
    "Cliente",
    "Caja",
    "Secuencia",
    "intervalo",
    "maq",
    "comentario",
    "ASeq",
    "operacion",
    "laborHedSeq"
  ],
  "include_header": true,
  "data": [
    {
      "Job": "J1001",
      "Part": "P-01",
      "Desc": "Etiqueta de prueba",
      "EMP": "E01",
      "Pa": "PA",
      "OP": "10",
      "Cantidad": 2,
      "Cliente": "ACME",
      "Caja": "C1",
      "Secuencia": "S1",
      "intervalo": "15",
      "maq": "BIXOLON",
      "comentario": "OK",
      "ASeq": "A1",
      "operacion": "SELLADO",
      "laborHedSeq": "LH100"
    }
  ]
}
```
enviroment
```
create a file .env
PORT=5002

```
- `destination` (string): ruta destino del CSV.
- `data` (objeto o lista de objetos): contenido JSON a convertir en filas.
- `columns` (opcional): orden exacto de columnas.
- `include_header` (opcional, default `true`): escribe o no encabezado.

Si no envías `columns`, se detectan automáticamente desde las llaves del JSON.

## 4) Ejemplo con curl

```bash
curl -X POST http://localhost:5000/csv \
  -H "Content-Type: application/json" \
  -d "{\"destination\":\"//10.100.2.54/SELLADOBIXOLON_TI$/EtiquetaTep.CSV\",\"data\":[{\"Job\":\"J1001\",\"Part\":\"P-01\"}]}"
```

## Notas de red/permiso

- El usuario del proceso Python debe tener permisos de escritura sobre el recurso compartido.
- Si ejecutas como servicio, valida la identidad del servicio (cuenta de dominio/servicio).
- El archivo se guarda con encoding `utf-8-sig` para buena compatibilidad en Excel.
