# Prompt de Análisis Post-Capítulo

Analiza el siguiente capítulo y extrae TODA la información narrativa relevante.

## ESTADO CONOCIDO DEL MUNDO ANTES DE ESTE CAPÍTULO
{{world_state_before}}

## PERSONAJES CONOCIDOS
{{characters_list}}

## HILOS ACTIVOS
{{active_threads}}

## PISTAS ACTIVAS
{{active_clues}}

## CAPÍTULO A ANALIZAR
{{chapter_content}}

---

## INSTRUCCIONES

Responde EXCLUSIVAMENTE en JSON válido, sin markdown ni texto adicional. Usa esta estructura exacta:

```json
{
  "summary": "Resumen de 2-3 frases del capítulo",
  "events": [
    {
      "type": "movement|death|discovery|destruction|transformation|revelation|encounter",
      "description": "Descripción del evento",
      "affected_characters": ["nombre_personaje"],
      "affected_objects": ["nombre_objeto"],
      "story_timestamp": "Fecha/hora en la historia si se menciona"
    }
  ],
  "knowledge_changes": [
    {
      "character_name": "Nombre del personaje",
      "fact": "Descripción del hecho que ahora sabe/sospecha",
      "new_knowledge_level": "knows|suspects|partial|wrong_belief",
      "how_learned": "witnessed|told_by:nombre|deduced|read|overheard"
    }
  ],
  "reader_knowledge_changes": [
    {
      "fact": "Hecho que el lector ahora sabe/sospecha",
      "new_knowledge_level": "knows|suspects|partial"
    }
  ],
  "thread_beats": [
    {
      "thread_name": "Nombre del hilo",
      "beat_type": "plant|reinforce|complicate|twist|escalate|near_reveal|reveal|resolve|subvert",
      "description": "Qué pasó con este hilo en el capítulo"
    }
  ],
  "clues": [
    {
      "description": "Descripción de la pista",
      "type": "verbal|visual|object|behavioral|environmental|structural|intertextual",
      "subtlety": 8,
      "mechanism": "Cómo funciona la pista",
      "related_thread": "Nombre del hilo relacionado o null"
    }
  ],
  "character_locations_end": [
    {
      "character_name": "Nombre",
      "location": "Dónde está al final del capítulo"
    }
  ],
  "character_emotional_states": [
    {
      "character_name": "Nombre",
      "emotional_state": "Estado emocional al final del capítulo"
    }
  ],
  "tension_level": 7,
  "scene_type": "action|dialogue|reflection|revelation|transition|flashback|confrontation|investigation",
  "pacing": "slow|medium|fast|frantic",
  "emotional_tone": "hopeful|dread|melancholy|triumphant|neutral|paranoid|intimate|chaotic",
  "opening_hook": "Cómo abre el capítulo",
  "closing_hook": "Cómo cierra el capítulo",
  "word_count": 3500,
  "notes": "Observaciones adicionales sobre consistencia, calidad, o sugerencias"
}
```

## REGLAS DE ANÁLISIS
1. Ser exhaustivo — extraer TODO lo que cambió, por sutil que sea.
2. Para knowledge_changes, solo incluir cambios REALES (no repetir lo que ya sabían).
3. Para clues, distinguir entre pistas intencionales y detalles decorativos.
4. Para thread_beats, solo incluir hilos que REALMENTE avanzaron en este capítulo.
5. El subtlety de pistas debe ser honesto — si es obvia, puntuar bajo.
6. Incluir SIEMPRE las ubicaciones de personajes al final del capítulo.
