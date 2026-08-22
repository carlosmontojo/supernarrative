# corpus/ — el activo real del proyecto

Aquí va todo el texto con el que se entrena Semilla. `prepare.py` lee
recursivamente cualquier `.txt` o `.md` de este directorio (este README se
excluye solo).

## Qué poner aquí

- **Texto propio, siempre que sea posible**: novelas, relatos, notas, ensayos,
  diarios. Es lo que hará que el modelo suene a ti y es el único ingrediente
  que nadie más puede aportar.
- **Dominio público en español** para dar volumen mientras el corpus propio
  crece. Ejemplo clásico (El Quijote, ~2MB, Proyecto Gutenberg):

  ```bash
  curl -o corpus/quijote.txt https://www.gutenberg.org/cache/epub/2000/pg2000.txt
  ```

## Reglas de higiene

1. **Un subdirectorio por fuente** cuando el corpus crezca
   (`corpus/propio/`, `corpus/dominio-publico/`, ...). La procedencia importa:
   la Fase 1 del roadmap pide poder pesar cada fuente por separado.
2. **Solo texto con derechos claros**: propio o dominio público. El corpus es
   para siempre; los problemas legales también.
3. **UTF-8 plano.** Sin PDF, sin docx: conviértelos antes de meterlos.

El contenido de este directorio **no se versiona en git** (ver .gitignore) —
haz copias de seguridad por tu cuenta: es la parte insustituible del proyecto.
