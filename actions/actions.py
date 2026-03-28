import os
import re
import json
import glob
import unicodedata
from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

def _normalize(text: str) -> str:
    """Devuelve el texto en minúsculas, sin acentos/diacríticos y sin espacios extra."""
    if not text:
        return ""
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def detectar_por_palabras(user_text: str) -> Optional[str]:
    """
    Busca en todos los JSON de data/tipos_violencia y retorna el nombre
    de archivo (p.ej. 'fisica.json') si alguna palabra_clave aparece en el texto.
    """
    carpeta = os.path.join("data", "tipos_violencia")
    u = _normalize(user_text)
    for ruta_json in glob.glob(os.path.join(carpeta, "*.json")):
        try:
            with open(ruta_json, encoding="utf-8") as f:
                datos = json.load(f)
            detector = (datos.get("detector_automatizado") or {})
            claves = (detector.get("palabras_clave") or [])
            claves_norm = [_normalize(c or "") for c in claves]
            if any(k and k in u for k in claves_norm):
                return os.path.basename(ruta_json)  # ej. "fisica.json"
        except Exception:
            continue
    return None


class ActionViolenceType(Action):
    def name(self) -> Text:
        return "action_answer_violence_type"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        intent = (tracker.latest_message.get("intent") or {}).get("name", "")
        user_text = (tracker.latest_message.get("text") or "").strip()  # <- conservamos tal cual

        # RESPUESTAS_CORTAS eliminado para permitir respuestas completas desde JSON

        mapping: Dict[str, Any] = {
            # Tipos
            "tipo_violencia_derechos_reproductivos": "derechos_reproductivos.json",
            "tipo_violencia_economica": "economica.json",
            "tipo_violencia_feminicida": "feminicida.json",
            "tipo_violencia_fisica": "fisica.json",
            "tipo_violencia_patrimonial": "patrimonial.json",
            "tipo_violencia_psicoemocional": "psicoemocional.json",
            "tipo_violencia_sexual": "sexual.json",

            # Señales
            "senales_alerta_control": "psicoemocional.json",
            "senales_alerta_aislamiento": "psicoemocional.json",
            "senales_alerta_desvalorizacion": "psicoemocional.json",
            "senales_alerta_celos_posesividad": "psicoemocional.json",
            "senales_alerta_minimizacion": "psicoemocional.json",
            "senales_alerta_culpabilizacion": "psicoemocional.json",
            "senales_alerta_excusas": "psicoemocional.json",
            "senales_alerta_miedo": "fisica.json",

            # Prevención
            "prevencion_general": ["psicoemocional.json", "fisica.json", "sexual.json", "feminicida.json"],
            "prevencion_autoproteccion": ["psicoemocional.json", "patrimonial.json"],
            "prevencion_hombres": ["psicoemocional.json", "fisica.json", "feminicida.json"],
            "prevencion_autocuidado": ["psicoemocional.json"],
            "prevencion_educacion": ["economica.json", "derechos_reproductivos.json", "feminicida.json"],
            "prevencion_trabajo": ["economica.json"],
            "prevencion_digital": ["sexual.json"],
            "prevencion_medios": ["sexual.json", "feminicida.json"],
            "prevencion_instituciones": ["feminicida.json"],

            # Instituciones (además de las respuestas cortas eliminadas)
            "instituciones_contacto_emergencia": "fisica.json",
            "instituciones_centros_justicia": "sexual.json",
            "instituciones_fiscalias_especializadas": "feminicida.json",
            "instituciones_inmujeres": "psicoemocional.json",
            "instituciones_cndh": "feminicida.json",
            "instituciones_organizaciones_civiles": "psicoemocional.json",
            "instituciones_general": "psicoemocional.json",

            # Consecuencias
            "consecuencias_psicologicas": "psicoemocional.json",
            "consecuencias_fisicas": "fisica.json",
            "consecuencias_sociales": "psicoemocional.json",
            "consecuencias_emocionales": "psicoemocional.json",
            "consecuencias_legales": "patrimonial.json",
            "consecuencias_largo_plazo": "psicoemocional.json",
            "consecuencias_ninas": "fisica.json",
            "consecuencias_comunidad": "feminicida.json",
            "consecuencias_derechos_rep": "derechos_reproductivos.json",

            # Acompañamiento
            "acompanamiento_general": "psicoemocional.json",
            "acompanamiento_general": "general.json",
            "acompanamiento_psicologico": "psicologico.json",
            "acompanamiento_legal": "legal.json",  # Asegúrate de crear data/tipos_violencia/legal.json
            "acompanamiento_psicologico": "psicoemocional.json",
            "acompanamiento_tiempos": "psicoemocional.json",
            "acompanamiento_proceso": "psicoemocional.json",
            "acompanamiento_acompanantes": "psicoemocional.json",
            "acompanamiento_seguimiento": "psicoemocional.json",

            # Otros
            "base_legal_fisica": "fisica.json",
            "faq_psicoemocional": "psicoemocional.json",
            "reconocimiento_sexual": "sexual.json",
            "recursos_feminicida": "feminicida.json",
            "frases_comunes_victima": "psicoemocional.json",
            "alerta_urgente": "urgente.json"
        }

        # --- Fallback por palabras clave si el intent no mapea ---
        archivo = mapping.get(intent)
        if not archivo:
            detectado = detectar_por_palabras(user_text)
            if detectado:
                archivo = detectado
            else:
                dispatcher.utter_message(text="Por ahora no tengo información para ese tema.")
                return []

        archivos = archivo if isinstance(archivo, list) else [archivo]

        # Función utilitaria: tokenización simple para matching de FAQs
        def tokens(s: str) -> set:
            return {w for w in re.findall(r"\w+", (s or "").lower()) if len(w) > 2}

        user_toks = tokens(user_text)

        for nombre_archivo in archivos:
            ruta = os.path.join("data", "tipos_violencia", nombre_archivo)
            try:
                with open(ruta, encoding="utf-8") as f:
                    datos = json.load(f)

                # 1) Señales
                if intent.startswith("senales_"):
                    senales = datos.get("senales_alerta", [])
                    if senales:
                        dispatcher.utter_message(text="Señales de alerta:")
                        for s in senales:
                            dispatcher.utter_message(text=f"- {s}")
                        return []

                # 2) Consecuencias
                if intent.startswith("consecuencias_"):
                    consecuencias = datos.get("consecuencias", [])
                    if consecuencias:
                        dispatcher.utter_message(text="Consecuencias:")
                        for c in consecuencias:
                            dispatcher.utter_message(text=f"- {c}")
                        return []

                # 3) Frases comunes
                if intent.startswith("frases_") or "comunes" in intent:
                    frases = datos.get("frases_comunes_victima", [])
                    if frases:
                        dispatcher.utter_message(text="Frases comunes en esta situación:")
                        for fz in frases:
                            dispatcher.utter_message(text=f"- \"{fz}\"")
                        return []

                # 4) Instituciones
                if intent.startswith("instituciones_"):
                    inst = datos.get("instituciones_apoyo", [])
                    if inst:
                        dispatcher.utter_message(text="Instituciones de apoyo:")
                        for i in inst:
                            dispatcher.utter_message(text=f"- {i}")
                        return []

                # 5) ¿Qué hacer? (acompañamiento)
                if intent.startswith("acompanamiento_"):
                    quehacer = datos.get("que_hacer", [])
                    if quehacer:
                        dispatcher.utter_message(text="¿Qué puedes hacer?")
                        for q in quehacer:
                            dispatcher.utter_message(text=f"- {q}")
                        return []

                # 6) Base legal
                if intent.startswith("base_legal") or "ley" in intent:
                    base = datos.get("base_legal", {})
                    if base:
                        dispatcher.utter_message(text="Base legal:")
                        for ley, texto in base.items():
                            dispatcher.utter_message(text=f"- *{ley}*: {texto}")
                        return []

                # 7) FAQs (MEJORA): intentar responder FAQ aunque el intent no sea "faq_*"
                faqs = datos.get("preguntas_frecuentes", [])
                if faqs and user_text:
                    best = None
                    best_score = 0
                    for fqa in faqs:
                        q = fqa.get("pregunta", "")
                        if not q:
                            continue
                        overlap = len(tokens(q) & user_toks)
                        if overlap > best_score:
                            best = fqa
                            best_score = overlap
                    # Umbral bajo pero útil: 2 palabras en común
                    if best and best_score >= 2:
                        dispatcher.utter_message(text="Preguntas frecuentes:")
                        pregunta = best.get("pregunta", "")
                        respuesta = best.get("respuesta", "")
                        if isinstance(respuesta, list):
                            dispatcher.utter_message(text=f"- {pregunta}\n" + "\n".join(respuesta))
                        else:
                            dispatcher.utter_message(text=f"- {pregunta}\n  {respuesta}")
                        return []

                # 8) Reconocimiento
                if intent.startswith("reconocimiento"):
                    texto = datos.get("reconocimiento", "")
                    if texto:
                        dispatcher.utter_message(text="¿Cómo reconocer esta violencia?")
                        dispatcher.utter_message(text=texto)
                        return []

                # 9) Recursos
                if intent.startswith("recursos") or "recurso" in intent:
                    recursos = datos.get("recursos", [])
                    if recursos:
                        dispatcher.utter_message(text="Recursos disponibles:")
                        for r in recursos:
                            tipo = r.get("tipo", "")
                            titulo = r.get("titulo", "")
                            url = r.get("url", "")
                            dispatcher.utter_message(
                                text=f"- {tipo.title()}: {titulo or 'Sin título'} ({url or 'sin enlace'})"
                            )
                        return []

                # 10) Respuesta base MEJORADA:
                #    - abre con "Eso es {Tipo}" o usa respuestas_chatbot.respuesta_directa si existe
                #    - luego Descripción, Alerta, Validación y Recomendación
                nombre = datos.get("nombre", nombre_archivo.replace(".json", ""))
                descripcion = datos.get("descripcion", "")
                alerta = datos.get("alerta", "")

                rc = (datos.get("respuestas_chatbot") or {})
                directa = rc.get("respuesta_directa") or f"Eso es {nombre}."
                validacion = rc.get("validacion")
                recomendacion = rc.get("recomendacion_general")

                # 10.1 Mensaje directo
                dispatcher.utter_message(text=directa)

                # 10.2 Descripción y alerta
                if descripcion:
                    dispatcher.utter_message(text=f"Descripción: {descripcion}")
                if alerta:
                    dispatcher.utter_message(text=f"Alerta: {alerta}")

                # 10.3 Validación y recomendación
                if validacion:
                    dispatcher.utter_message(text=validacion)

                if recomendacion:
                    if isinstance(recomendacion, list):
                        for linea in recomendacion:
                            dispatcher.utter_message(text=str(linea))
                    else:
                        dispatcher.utter_message(text=recomendacion)

            except Exception as e:
                dispatcher.utter_message(text=f"Hubo un problema al acceder al archivo: {nombre_archivo}")
                print(e)

        return []
