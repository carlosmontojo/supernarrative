# corpus/ — el activo real del proyecto

Aquí va todo el texto con el que se entrena Semilla. `prepare.py` lee
recursivamente cualquier `.txt` o `.md` de este directorio (este README se
excluye solo).

## Las cuatro capas del corpus del CFO

1. **Legislación y normativa (dominio público)** — se descarga con `boe.py`:

   ```bash
   # Fiscal
   python boe.py BOE-A-2006-20764   # Ley 35/2006, IRPF
   python boe.py BOE-A-1992-28740   # Ley 37/1992, IVA
   python boe.py BOE-A-2014-12328   # Ley 27/2014, Impuesto sobre Sociedades
   python boe.py BOE-A-2003-23186   # Ley 58/2003, General Tributaria
   # Contabilidad y gestión
   python boe.py BOE-A-2007-19884   # RD 1514/2007, Plan General de Contabilidad
   python boe.py BOE-A-2007-19966   # RD 1515/2007, PGC de PYMES
   python boe.py BOE-A-2012-14696   # RD 1619/2012, Reglamento de facturación
   python boe.py BOE-A-2004-21830   # Ley 3/2004, morosidad (plazos de pago)
   ```

   Los textos legales españoles no tienen derechos de autor (art. 13 LPI).

2. **Doctrina y práctica** (`corpus/doctrina/`): consultas vinculantes de la
   DGT, resoluciones del TEAC, manuales de la AEAT y del ICAC. Público;
   etiquetar procedencia y fecha, porque en fiscal la vigencia lo es todo.

3. **Contenido propio de Quentax** (`corpus/quentax/`): documentación, FAQs,
   respuestas de soporte, explicaciones a clientes. **Es la capa que nadie
   más puede tener** y la que hará que el modelo suene a Quentax.

4. **Datos operativos de Quentax** (`corpus/operativa/`): ejemplos anonimizados
   de trabajo real de CFO — conciliaciones resueltas (movimiento, factura y por
   qué casan), categorizaciones de gasto a cuenta del PGC, decisiones de
   tesorería. Es la capa que convierte "sabe de fiscal" en "sabe ser CFO", y se
   captura desde el propio producto: cada corrección de un usuario es un dato
   etiquetado por un experto.

**Anonimización obligatoria en las capas 3 y 4**: ni nombres, ni NIFs, ni datos
de clientes. El corpus se entrena para siempre; los datos personales no se
borran de unos pesos.

## Reglas de higiene

1. **Un subdirectorio por fuente** (`corpus/boe/`, `corpus/doctrina/`,
   `corpus/quentax/`). La procedencia importa: la Fase 1 pide poder pesar
   cada fuente por separado.
2. **Solo texto con derechos claros** y **sin datos personales**.
3. **UTF-8 plano.** Sin PDF, sin docx: conviértelos antes de meterlos.

El contenido de este directorio **no se versiona en git** (ver .gitignore) —
haz copias de seguridad por tu cuenta: es la parte insustituible del proyecto.
