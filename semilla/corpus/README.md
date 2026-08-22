# corpus/ — el activo real del proyecto

Aquí va todo el texto con el que se entrena Semilla. `prepare.py` lee
recursivamente cualquier `.txt` o `.md` de este directorio (este README se
excluye solo).

## Las tres capas del corpus fiscal

1. **Legislación (dominio público)** — se descarga con `boe.py`:

   ```bash
   python boe.py BOE-A-2006-20764   # Ley 35/2006, IRPF
   python boe.py BOE-A-1992-28740   # Ley 37/1992, IVA
   python boe.py BOE-A-2014-12328   # Ley 27/2014, Impuesto sobre Sociedades
   python boe.py BOE-A-2003-23186   # Ley 58/2003, General Tributaria
   ```

   Los textos legales españoles no tienen derechos de autor (art. 13 LPI).

2. **Doctrina y práctica** (`corpus/doctrina/`): consultas vinculantes de la
   DGT, resoluciones del TEAC, manuales de la AEAT. Público; etiquetar
   procedencia y fecha, porque en fiscal la vigencia lo es todo.

3. **Contenido propio de Quentax** (`corpus/quentax/`): documentación, FAQs,
   respuestas de soporte, explicaciones a clientes. **Es la capa que nadie
   más puede tener** y la que hará que el modelo suene a Quentax. Antes de
   meter nada aquí: anonimizar — ni nombres, ni NIFs, ni datos de clientes.
   El corpus se entrena para siempre; los datos personales no se borran de
   unos pesos.

## Reglas de higiene

1. **Un subdirectorio por fuente** (`corpus/boe/`, `corpus/doctrina/`,
   `corpus/quentax/`). La procedencia importa: la Fase 1 pide poder pesar
   cada fuente por separado.
2. **Solo texto con derechos claros** y **sin datos personales**.
3. **UTF-8 plano.** Sin PDF, sin docx: conviértelos antes de meterlos.

El contenido de este directorio **no se versiona en git** (ver .gitignore) —
haz copias de seguridad por tu cuenta: es la parte insustituible del proyecto.
